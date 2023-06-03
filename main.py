import logging
from xml.dom import ValidationErr

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain.chains import LLMChain
from langchain.llms import OpenAI

from callback import StreamingLLMCallbackHandler
from models.schemas import ChatMessage
from models.schemas import MessageSender
from models.schemas import MessageType
from fastapi.middleware.cors import CORSMiddleware
import socketio
import pickle
from pathlib import Path
from typing import Optional
from langchain.vectorstores import VectorStore
from langchain.chat_models import ChatOpenAI

vectorstore: Optional[VectorStore] = None


load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# #TODO: Check if cors is needed after angular is added to static.
origins = ["http://localhost:4200"]

sio: socketio.AsyncServer = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)
socketio_app = socketio.ASGIApp(sio, app)
app.mount("/", socketio_app)


app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)
from langchain.prompts import PromptTemplate

@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    if not Path("vectorstore.pkl").exists():
        raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
    with open("vectorstore.pkl", "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # logging.info("*********In ReadRoot:")
    return templates.TemplateResponse("index.html", {"request": request})


@sio.event
def connect(sid, environ):
    # logging.info("**********Connected.")
    print("connect ", sid)


@sio.event
async def message(sid, data):
    print("message ", data)
    # logging.info(f"********* message received: {data} ")
    await sio.emit("message", data, room=sid)


@sio.event
def disconnect(sid):
    logging.info(f"**********Disconnected. {sid}")


# WebSocket endpoint
@sio.on("chat")
async def chat(sid, data):
    # logging.info(f"**********Received a message in chat {data}")
    try:
        cm = ChatMessage(**data)
    except ValidationErr as e:
        logging.error(e)
    #TODO: Add chat history
    reinterpretedQuestion = await generate_question(cm.message, "")
    # TODO: add number of docs fetched. 
    docs = await queryDocs(reinterpretedQuestion, vectorstore, 2)
    chain: LLMChain = await createChain(sid, sio) #TODO: fix the parameters passed. 
    await chain.arun({
        'question': reinterpretedQuestion, 
        'context' : docs,
        'chat_history': ""
        })
    # logging.info("Chain complete. ")
    end_resp = ChatMessage(
        sender=MessageSender.AI, message="", type=MessageType.STREAM_END
    )
    await sio.emit("chat", end_resp.toJson(), room=sid)
    # TODO: change format of this command message.
    command_msg = ChatMessage(
        sender=MessageSender.AI, message="home", type=MessageType.COMMAND
    )
    await sio.emit("chat", command_msg.toJson(), room=sid)
    # logging.info("Done. ")

# TODO: maybe simplify this method to take in less params
async def createChain(sid: str, sio: socketio.AsyncServer):
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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
