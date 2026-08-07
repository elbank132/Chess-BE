import socketio
import uvicorn

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)


app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"🟢 Client connected: {sid}")
    
@sio.event
async def disconnect(sid):
    print(f"🔴 Client disconnected: {sid}")

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)