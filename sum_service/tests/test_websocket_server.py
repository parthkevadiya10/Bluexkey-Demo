import pytest
import asyncio
import websockets
import json
import grpc
import sum_pb2
import sum_pb2_grpc
from sum_service.websocket.server import WebSocketServer

@pytest.fixture
async def websocket_server():
    server = WebSocketServer(grpc_host='localhost', grpc_port=50051)
    return server

@pytest.mark.asyncio
async def test_websocket_connection(websocket_server):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Test sending first number
        first_number = {"number": 5}
        await websocket.send(json.dumps(first_number))
        response = await websocket.recv()
        response_data = json.loads(response)
        assert "message" in response_data
        assert "Received number 5" in response_data["message"]

        # Test sending second number
        second_number = {"number": 3}
        await websocket.send(json.dumps(second_number))
        response = await websocket.recv()
        response_data = json.loads(response)
        assert "result" in response_data
        assert response_data["result"] == 8
        assert "numbers" in response_data
        assert response_data["numbers"] == [5, 3]

@pytest.mark.asyncio
async def test_invalid_request(websocket_server):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Test invalid request
        invalid_data = {"invalid": "data"}
        await websocket.send(json.dumps(invalid_data))
        response = await websocket.recv()
        response_data = json.loads(response)
        assert "error" in response_data
        assert "Invalid request" in response_data["error"] 