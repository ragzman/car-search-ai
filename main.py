from xml.dom import ValidationErr
from fastapi import FastAPI, Request, WebSocket
import logging
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from langchain.llms import OpenAI
from models.schemas import ChatResponse


load_dotenv()  # Load environment variables from .env file

app = FastAPI()

app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")

#TODO(Aditya): fix logging config location.
logging.basicConfig(level=logging.INFO)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket endpoint
@app.websocket("/aichat")
async def websocket_endpoint(websocket: WebSocket):
    llm = OpenAI(temperature=0.9)
    await websocket.accept()
    

    while True:
        try:
            # Receive message from frontend
            data = await websocket.receive_json()
            # Validate and process the received message
            try:
                logging.info(data)
                cm = ChatResponse(**data)  #TODO(Aditya): rename this class from ChatResponse to something like ChatSchema.ß
            except ValidationErr as e:
                await websocket.send_json({"error": str(e)})
                continue

            botResponse = llm(cm.message)
            response = ChatResponse(sender= "bot", message = botResponse, type = "stream") # TODO Use other message types etc.
            logging.info(response)
            await websocket.send_json(response.json())

        except WebSocketDisconnect:
            break

    await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
