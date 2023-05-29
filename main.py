import logging
from xml.dom import ValidationErr

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain.chains import LLMChain
from langchain.llms import OpenAI

from callback import StreamingLLMCallbackHandler
from models.schemas import ChatResponse

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

# TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)
from langchain.prompts import PromptTemplate


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# WebSocket endpoint
@app.websocket("/aichat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chain: LLMChain = createChain(websocket=websocket)
    while True:
        try:
            # Receive message from frontend
            data = await websocket.receive_json()
            # Validate and process the received message
            try:
                logging.info(data)  # TODO: remove logging.
                cm = ChatResponse(
                    **data
                )  # TODO(Aditya): rename this class from ChatResponse to something like ChatSchema.ß
            except ValidationErr as e:
                await websocket.send_json({"error": str(e)})
                continue

            botResponse = await chain.arun(cm.message)
            logging.info(f"The message received is {botResponse}")

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.toJson())
        except WebSocketDisconnect:
            break

    await websocket.close()

def createChain(websocket):
    stream_handler = StreamingLLMCallbackHandler(websocket)
    llm = OpenAI(temperature=0.9, streaming=True, callbacks=[stream_handler], verbose= True)
    prompt = PromptTemplate(
        input_variables=["product"],
        template="What is a good name for a company that makes {product}?",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
