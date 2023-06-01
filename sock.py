from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import socketio

# Create FastAPI app
app = FastAPI()

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi')
socket_app = socketio.ASGIApp(sio, static_files={"/": "index.html"})

# Define WebSocket event handlers
@sio.on('connect')
async def connect(sid, environ):
    print(f'Client connected: {sid}')

@sio.on('disconnect')
async def disconnect(sid):
    print(f'Client disconnected: {sid}')

@sio.on('echo')
async def echo(sid, message):
    await sio.emit('echo', message, room=sid)

# Define FastAPI routes
@app.get('/')
async def index():
    with open('index.html') as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.websocket('/socket.io')
async def websocket_endpoint(websocket):
    await socket_app.handle_request(websocket)

# Run the application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
