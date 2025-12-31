from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from .game_logic import generate_board

app = FastAPI()

# CORS configuration
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO configuration
# cors_allowed_origins="*" allows all origins
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Wrap FastAPI app with Socket.IO
# The 'app' variable appearing here will be overwritten, so let's be careful.
# Actually, let's keep 'app' as FastAPI for clarity in decorators, 
# and expose 'socket_app' as the ASGI entry point, 
# BUT the user command is `uvicorn backend.main:app`.
# So we must assign the final ASGI app to `app`.

fastapi_app = app
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)

@fastapi_app.get("/")
async def root():
    return {"message": "Catan Backend is running. Access /api/board for game data."}

@fastapi_app.get("/api/board")
async def get_board():
    return generate_board()

@sio.event
async def connect(sid, environ):
    print("connect ", sid)
    # Send State
    from .game_logic import game_manager
    await sio.emit('board_state', game_manager.board.model_dump(), to=sid)
    await sio.emit('game_state', game_manager.state.model_dump(), to=sid)

@sio.event
async def build_settlement(sid, data):
    from .game_logic import game_manager
    # data: { q, r, corner }
    success = game_manager.build_settlement(data['q'], data['r'], data['corner'])
    if success:
        await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def build_road(sid, data):
    from .game_logic import game_manager
    # data: { q, r, edge }
    success = game_manager.build_road(data['q'], data['r'], data['edge'])
    if success:
        await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def build_city(sid, data):
    from .game_logic import game_manager
    # Expects {'q': q, 'r': r, 'corner': c}
    success = game_manager.build_city(data['q'], data['r'], data['corner'])
    if success:
        await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def roll_dice(sid):
    from .game_logic import game_manager
    # Check if it is the current player's turn? (Skipping strict validation for MVP speed, but should exist)
    total = game_manager.roll_dice()
    print(f"Rolled {total}")
    await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def end_turn(sid):
    from .game_logic import game_manager
    game_manager.end_turn()
    await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def test_resources(sid):
    from .game_logic import game_manager
    game_manager.cheat_resources()
    await sio.emit('game_state', game_manager.state.model_dump())

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)
