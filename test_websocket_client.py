import asyncio
import websockets
import json

async def main():
    uri = "ws://localhost:8765"
    print("Connecting to WebSocket...")
    async with websockets.connect(uri) as websocket:
        for i in range(1, 6):
            # Send number
            message = {"number": i}
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}", end=", ")

            # Receive response
            response = await websocket.recv()
            print(f"Received: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 