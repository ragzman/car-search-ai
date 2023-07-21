import logging
from langchain import LLMChain, OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import VectorStore
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory

from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import boto3
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory

load_dotenv()  # Load environment variables from .env file

dynamodb = boto3.resource('dynamodb')

# # Create the DynamoDB table.
# table = dynamodb.create_table(
#     TableName='SessionTable',
#     KeySchema=[
#         {
#             'AttributeName': 'SessionId',
#             'KeyType': 'HASH'
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'SessionId',
#             'AttributeType': 'S'
#         }
#     ],
#     BillingMode='PAY_PER_REQUEST',
# )

# Wait until the table exists.
# table.meta.client.get_waiter('table_exists').wait(TableName='SessionTable')


CONDENSE_PROMPT = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

# TODO: add URLs in the prompt.
# Always return the url fields from the context in the answer as markdown links associated to the title of the blog or name of product.
HUMAN_MSG_TEMPLATE = """You are provided a "Question" from our users, some related content from our website as "Context" and previous chat history as "History".
Context: {context}
Question: {question}
Provide an answer to the Question based on the context. Limit your answer to 300 words. 
You should only use urls that are explicitly listed as a url in the context. Do NOT make up a URL that is not listed.
If you don't know the answer, nudge the user for more information. Always be friendly and helpful.
Answer in Markdown. Use bullets and headings to help clarify the content. """

system_message_prompt = SystemMessagePromptTemplate.from_template(
    "You are an AI assistant for www.holthelaw.com . You provide helpful information on Canada Immigration related questions."
)
human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_MSG_TEMPLATE)

chat_prompt = ChatPromptTemplate.from_messages(
    [
        system_message_prompt,
        # MessagesPlaceholder(variable_name="history"),
        human_message_prompt,
    ]
)

# TODO: check temperature.
chatModel = ChatOpenAI(
    temperature=0,
    streaming=True,
    verbose=True,
)


# TODO: maybe simplify this method to take in less params
def createChain(sid: str):
    """Create the langhcain chain."""
    chat_history = DynamoDBChatMessageHistory(
        table_name="SessionTable",
        session_id=sid,
    )
    #TODO: limit the number of items in memory.
    memoryDB = ConversationBufferMemory(
        return_messages=True,
        memory_key="history",
        input_key="question",
        chat_memory=chat_history,
    )

    chain = LLMChain(
        llm=chatModel,
        prompt=chat_prompt,
        verbose=True,
        memory=memoryDB,
    )
    return chain


async def generate_question(user_input: str, chat_history: str) -> str:
    if chat_history.strip() == "":
        logging.info(f"Chat history is empty. not reinterpretting the question.")
        return user_input
    prompt = PromptTemplate(
        template=CONDENSE_PROMPT, input_variables=["question", "chat_history"]
    )
    # TODO: fix this chain type. should be conversationChain after that bug is fixed.
    # https://github.com/hwchase17/langchain/pull/2515
    chain = LLMChain(llm=chatModel, prompt=prompt)
    res = await chain.arun(question=user_input, chat_history=chat_history)
    logging.info(f"Debug: ReInterpreted question: {res}")
    return res


async def queryDocs(updatedQuestion: str, vectorStore: VectorStore, k: int):
    docs = vectorStore.similarity_search(updatedQuestion, k=k)
    # logging.info(f"similarity search returned : {docs}")
    # content = [d.page_content for d in docs]
    return docs  # TODO: maybe concat better.
