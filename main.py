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
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)
# app = web.Application()
# sio.attach(app)

# sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=origins)

socketio_app = socketio.ASGIApp(sio, app)
app.mount("/", socketio_app)


app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)
from langchain.prompts import PromptTemplate


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logging.info("*********In ReadRoot:")
    return templates.TemplateResponse("index.html", {"request": request})


@sio.event
def connect(sid, environ):
    logging.info("**********Connected.")
    print("connect ", sid)

@sio.event
async def message(sid, data):
    print("message ", data)
    logging.info(f"********* message received: {data} ")

@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    logging.info("**********Disconnected.")


# WebSocket endpoint
@app.websocket("/aichat")
async def websocket_endpoint(websocket: WebSocket):
    logging.info(f'**********Received a message -- Addy')
    await sio.app.handle_request(websocket.scope, websocket.receive, websocket.send)
    # await websocket.accept()
    # chain: LLMChain = createChain(websocket=websocket)
    # while True:
    #     try:
    #         # Receive message from frontend
    #         data = await websocket.receive_json()
    #         # Validate and process the received message
    #         try:
    #             logging.info(data)  # TODO: remove logging.
    #             cm = ChatMessage.fromJson(data)
    #         except ValidationErr as e:
    #             await websocket.send_json({"error": str(e)})
    #             continue
    #         if cm.type == MessageType.CLIENT_QUESTION:
    #             await chain.arun(cm.message)
    #         else:
    #             #TODO: does the client need to send any other type of message?
    #             logging.info(f"The message received is {cm.toJson()}")

    #         end_resp = ChatMessage(
    #             sender=MessageSender.AI, message="", type=MessageType.STREAM_END
    #         )
    #         await websocket.send_json(end_resp.toJson())
    #     except WebSocketDisconnect:
    #         break

    # await websocket.close()


def createChain(websocket):
    """Create the langhcain chain. """
    stream_handler = StreamingLLMCallbackHandler(websocket)
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


# class AIChatNamespace(AsyncNamespace):
#     async def on_connect(self, sid, environ):
#         logging.info(sid)
#         logging.info("*********Client connected in AINamespace:", sid)

#         await self.emit("message", "Welcome to the chat!", room=sid)

#     async def on_message(self, sid, data):
#         # Validate and process the received message
#         try:
#             logging.info(data)  # TODO: remove logging.
#             cm = ChatMessage.fromJson(data)
#         except ValidationErr as e:
#             await self.emit("error", str(e), room=sid)
#             return
#         if cm.type == MessageType.CLIENT_QUESTION:
#             chain = createChain()
#             await chain.arun(cm.message)
#         else:
#             # TODO: does the client need to send any other type of message?
#             logging.info(f"The message received is {cm.toJson()}")

#         end_resp = ChatMessage(
#             sender=MessageSender.AI, message="", type=MessageType.STREAM_END
#         )
#         await self.emit("message", end_resp.toJson(), room=sid)

#     async def on_disconnect(self, sid):
#         print("Client disconnected:", sid)

#     def createChain(self):
#         """Create the langhcain chain. """
#         stream_handler = StreamingLLMCallbackHandler(self)
#         llm = OpenAI(
#             temperature=0.9, streaming=True, callbacks=[stream_handler], verbose=True
#         )
#         prompt = PromptTemplate(
#             input_variables=["question"],
#             template="Answer the user's question in a couple of lines. Question:  {question}?",
#         )
#         chain = LLMChain(llm=llm, prompt=prompt)
#         return chain

