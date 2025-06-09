import asyncio
import websockets
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_client():
    # Get configuration from environment variables
    ws_host = os.getenv('WS_HOST', 'localhost')
    ws_port = os.getenv('WS_PORT', '8765')
    uri = f"ws://{ws_host}:{ws_port}"
    
    logger.info(f"Connecting to WebSocket server at {uri}")
    
    async with websockets.connect(uri) as websocket:
        # Test sending numbers
        test_numbers = [1, 2, 3, 4, 5]
        
        for number in test_numbers:
            # Send number
            message = json.dumps({"number": number})
            logger.info(f"Sending: {message}")
            await websocket.send(message)
            
            # Get response
            response = await websocket.recv()
            logger.info(f"Received: {response}")
            
            # Small delay between requests
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_websocket_client()) 