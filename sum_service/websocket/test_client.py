import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://websocket-server:8765"
    async with websockets.connect(uri) as websocket:
        # Test sending first number
        first_number = {"number": 5}
        print(f"Sending first number: {first_number}")
        await websocket.send(json.dumps(first_number))
        response = await websocket.recv()
        print(f"Received response: {response}")

        # Test sending second number
        second_number = {"number": 3}
        print(f"\nSending second number: {second_number}")
        await websocket.send(json.dumps(second_number))
        response = await websocket.recv()
        print(f"Received response: {response}")

        # Test invalid request
        invalid_data = {"invalid": "data"}
        print(f"\nSending invalid request: {invalid_data}")
        await websocket.send(json.dumps(invalid_data))
        response = await websocket.recv()
        print(f"Received response: {response}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 