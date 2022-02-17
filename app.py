import json
import random
import signal
import uvloop
import asyncio
import structlog
import websockets
from typing import Any, Dict

from bot import Bot, Direction
import config


logger = structlog.get_logger()


CONNECTED_BOTS = {}

# Should get with session_list
ROWS = 50
COLS = 100


async def handle_tick(data: Dict, websocket: Any):
    snakes = data['snakes']
    apples = data['apples']
    deaths = data['deaths']

    # Remove dead bots
    for user_id in deaths:
        if user_id in CONNECTED_BOTS:
            logger.warning(f'[BOT DEATH] {user_id}')
            del CONNECTED_BOTS[user_id]

    # Prepare board
    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for snake_id, data in snakes.items():
        cells = data['cells']
        for cell in cells:
            board[cell[0]][cell[1]] = 1
    for apple in apples:
        board[apple[0]][apple[1]] = 2

    # Make bot moves
    for bot_id, bot_instance in CONNECTED_BOTS.items():
        move = bot_instance.move(
            Direction(snakes[bot_id]['direction']),
            snakes[bot_id]['cells'],
            board
        )
        if move is not None:
            event = {
                'type': 'play',
                'user_id': bot_instance.bot_id,
                'direction': move.value
            }
            await websocket.send(json.dumps(event))


async def spawn_bots(websocket: Any):
    while len(CONNECTED_BOTS) < config.NR_BOTS:
        session_id = 'test'
        await connect_new_bot(websocket, session_id)


async def connect_new_bot(websocket: Any, session_id: str):
    bot_id = str(random.randint(0, 10 ** 9))
    event = {
        'type': 'join',
        'user_id': bot_id,
        'session_id': session_id,
    }
    logger.info(f'Connected new bot {event}')
    CONNECTED_BOTS[bot_id] = Bot(bot_id)
    await websocket.send(json.dumps(event))


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    logger.info(f'Connecting to {config.WEBSOCKET_URL}')
    async for websocket in websockets.connect(config.WEBSOCKET_URL):
        try:
            # Get session list
            await websocket.send(
                json.dumps({
                    'type': 'session_list',
                })
            )
            session_list = await websocket.recv()
            session_list = json.loads(session_list)
            logger.info('Got session list from server')

            await spawn_bots(websocket)

            async for message in websocket:
                tick = json.loads(message)
                await handle_tick(tick, websocket)
                await spawn_bots(websocket)

        except websockets.ConnectionClosed:
            ...


if __name__ == '__main__':
    uvloop.install()
    asyncio.run(main())
