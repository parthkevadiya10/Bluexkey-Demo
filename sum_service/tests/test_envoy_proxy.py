import pytest
import asyncio
import websockets
import json
import os
import time
import grpc
from concurrent.futures import ThreadPoolExecutor

# Constants
ENVOY_WS_URL = "ws://localhost:8765"
TEST_NUMBERS = [1, 2, 3, 4, 5]

async def wait_for_services():
    """Wait for services to be ready"""
    max_retries = 30
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            # Try to connect to gRPC server
            channel = grpc.insecure_channel('localhost:50051')
            await asyncio.sleep(0.1)  # Give time for connection
            return True
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries}: Waiting for services... Error: {str(e)}")
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
            continue
    return False

async def connect_websocket():
    """Establish WebSocket connection to Envoy proxy"""
    max_retries = 5
    retry_delay = 1
    
    for i in range(max_retries):
        try:
            websocket = await websockets.connect(ENVOY_WS_URL)
            return websocket
        except Exception as e:
            print(f"WebSocket connection attempt {i+1}/{max_retries} failed: {str(e)}")
            if i < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                raise

async def send_number(websocket, number):
    """Send a number through WebSocket and get response"""
    message = json.dumps({"number": number})
    print(f"Sending: {message}")
    await websocket.send(message)
    response = await websocket.recv()
    print(f"Received: {response}")
    return json.loads(response)

@pytest.mark.asyncio
async def test_envoy_websocket_to_grpc():
    """Test WebSocket to gRPC conversion through Envoy proxy"""
    # Wait for services to be ready
    if not await wait_for_services():
        pytest.fail("Services not ready after timeout")
    
    websocket = None
    try:
        websocket = await connect_websocket()
        for number in TEST_NUMBERS:
            response = await send_number(websocket, number)
            
            # Verify response format
            assert "result" in response, "Response should contain 'result' field"
            assert isinstance(response["result"], (int, float)), "Result should be a number"
            
            # Verify calculation (sum of numbers from 1 to n)
            expected_sum = sum(range(1, number + 1))
            assert response["result"] == expected_sum, \
                f"Expected sum {expected_sum} for number {number}, got {response['result']}"
    finally:
        if websocket:
            await websocket.close()

@pytest.mark.asyncio
async def test_envoy_websocket_error_handling():
    """Test error handling in WebSocket to gRPC conversion"""
    # Wait for services to be ready
    if not await wait_for_services():
        pytest.fail("Services not ready after timeout")
    
    websocket = None
    try:
        websocket = await connect_websocket()
        # Test invalid JSON
        print("Testing invalid JSON...")
        await websocket.send("invalid json")
        response = await websocket.recv()
        print(f"Received: {response}")
        response_data = json.loads(response)
        assert "error" in response_data, "Should receive error for invalid JSON"
        
        # Test missing number field
        print("Testing missing number field...")
        await websocket.send(json.dumps({"invalid": "data"}))
        response = await websocket.recv()
        print(f"Received: {response}")
        response_data = json.loads(response)
        assert "error" in response_data, "Should receive error for missing number field"
    finally:
        if websocket:
            await websocket.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 