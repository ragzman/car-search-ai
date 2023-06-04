import logging
from xml.dom import ValidationErr

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain import LLMChain
from ai.query import createChain, generate_question, queryDocs
from langchain.chains import ConversationChain
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

vectorstore: Optional[VectorStore] = None


load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# #TODO: Check if cors is needed after angular is added to static.
origins = ["http://localhost:4200"]

sio: socketio.AsyncServer = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=origins
)
socketio_app = socketio.ASGIApp(sio, app)
app.mount("/", socketio_app)


app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)


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
    # TODO: Add chat history
    reinterpretedQuestion = await generate_question(cm.message, "")
    # TODO: add number of docs fetched.
    # TODO: metadata from the fetched docs is thrown away. let's get URLs from there.
    k = 2
    docs = await queryDocs(reinterpretedQuestion, vectorstore, k)

    chain: ConversationChain = createChain(sid)
    await chain.acall(
        {"question": reinterpretedQuestion, "context": docs},
        callbacks=[StreamingLLMCallbackHandler(sid, sio)],
    )
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


# TODO: add a page for bot-first-website-design

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
