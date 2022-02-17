import os


NR_BOTS = int(os.environ.get('NR_BOTS', 3))
WEBSOCKET_URL = os.environ.get('WEBSOCKET_URL', 'ws://localhost:8001')
