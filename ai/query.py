import logging
from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from callback import StreamingLLMCallbackHandler
from socketio import AsyncServer
from langchain.chains import LLMChain
from langchain.vectorstores import VectorStore
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file


#TODO: add URLs in the prompt.
QA_PROMPT = """You are an AI assistant for Chatables.ai. We are a company that builds AI based chatbots.
You are provided a "Question" from our users, some related content from our website as "Context" and previous chat history as "History".
Provide a conversational answer to the user's question based on the information in the context.
If you don't know the answer, nudge the user for more information. Always be friendly and helpful.
Context: {context}
Question: {question}
History : {chat_history}
Limit your answer to 125 words. Always return URLs in the answer as markdown links associated to the title of the blog or name of product.
Answer in Markdown:"""


CONDENSE_PROMPT = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:""";


# TODO: check temperature. 
chatModel = ChatOpenAI(
  temperature= 0,
  streaming= True,
  verbose= True,
)


# TODO: maybe simplify this method to take in less params
async def createChain(sid: str, sio: AsyncServer):
    """Create the langhcain chain."""
    stream_handler = StreamingLLMCallbackHandler(sid, sio)
    # fix the llm used here. 
    llm = OpenAI(
        temperature=0.9, streaming=True, callbacks=[stream_handler], verbose=True
    )
    prompt = PromptTemplate(
        input_variables=["question", "context", "chat_history"],
        template=QA_PROMPT,
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain

async def generate_question(user_input: str, chat_history: str) -> str:
    if(chat_history.strip() == ""):
        logging.info(f'Chat history is empty. not reinterpretting the question.')
        return user_input
    prompt = PromptTemplate(
        template=CONDENSE_PROMPT,
        input_variables=["question", "chat_history"]
    )
    chain = LLMChain(llm=chatModel, prompt=prompt)
    res = await chain.arun(question =  user_input, chat_history= chat_history)
    logging.info(f"Debug: ReInterpreted question: {res}")
    return res

async def queryDocs(updatedQuestion: str, vectorStore: VectorStore, k: int):
    docs = vectorStore.similarity_search(updatedQuestion, k=k)
    logging.info(f'similarity search returned : {docs}')
    content = [d.page_content for d in docs]
    return "  ".join(content) #TODO: maybe concat better. 