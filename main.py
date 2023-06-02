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


load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# #TODO: Check if cors is needed after angular is added to static.
origins = ["http://localhost:4200"]

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)
socketio_app = socketio.ASGIApp(sio, app)
app.mount("/", socketio_app)


app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)
from langchain.prompts import PromptTemplate


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
    chain: LLMChain = createChain(sid, sio)
    await chain.arun(cm.message)
    # logging.info("Chain complete. ")
    end_resp = ChatMessage(
        sender=MessageSender.AI, message="", type=MessageType.STREAM_END
    )
    await sio.emit("chat", end_resp.toJson(), room=sid)
    # logging.info("Done. ")


def createChain(sid, sio):
    """Create the langhcain chain."""
    stream_handler = StreamingLLMCallbackHandler(sid, sio)
    llm = OpenAI(
        temperature=0.9, streaming=True, callbacks=[stream_handler], verbose=True
    )
    prompt = PromptTemplate(
        input_variables=["question"],
        template="Answer the user's question in a couple of lines. Question:  {question}?",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
