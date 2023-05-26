from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="dist"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket endpoint
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            # Receive message from frontend
            message = await websocket.receive_json()
            message_type = message.get("type")
            message_text = message.get("text")

            if message_type == "user":
                # Process user input and generate bot response
                # Replace this with your chatbot logic
                bot_response = f"This is the bot's response to: {message_text}"

                # Send bot response to frontend
                response = {"type": "bot", "text": bot_response}
                await websocket.send_json(response)

        except WebSocketDisconnect:
            break

    await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
