import asyncio
import websockets
import grpc
import pytest
import json
from concurrent import futures
import time
import logging
import os
import sys

# Add proto directory to Python path
proto_dir = os.path.join(os.path.dirname(__file__), 'sum_service', 'grpc', 'proto')
sys.path.append(proto_dir)

# Import generated proto files
from sum_pb2 import SumRequest, SumResponse
from sum_pb2_grpc import SumServiceStub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
WEBSOCKET_URL = "ws://localhost:8765"
GRPC_HOST = "localhost"
GRPC_PORT = 50051

async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            logger.info("Successfully connected to WebSocket server")
            
            # Test sending numbers and receiving sums
            test_numbers = [1, 2, 3, 4, 5]
            expected_sums = [1, 3, 6, 10, 15]
            
            for num, expected_sum in zip(test_numbers, expected_sums):
                # Send number
                await websocket.send(json.dumps({"number": num}))
                logger.info(f"Sent number: {num}")
                
                # Receive response
                response = await websocket.recv()
                response_data = json.loads(response)
                
                # Verify response
                assert "sum" in response_data, "Response missing 'sum' field"
                assert response_data["sum"] == expected_sum, f"Expected sum {expected_sum}, got {response_data['sum']}"
                logger.info(f"Received correct sum: {response_data['sum']}")
                
                # Small delay between messages
                await asyncio.sleep(0.1)
            
            logger.info("WebSocket test completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"WebSocket test failed: {str(e)}")
        return False

async def test_grpc_connection():
    """Test direct gRPC connection and communication"""
    try:
        # Create gRPC channel
        channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        
        # Create stub
        stub = SumServiceStub(channel)
        
        # Reset the sum before starting the test
        request = SumRequest(number=0)
        stub.ResetSum(request)
        logger.info("Reset gRPC server sum to 0")
        
        # Test sending numbers
        test_numbers = [1, 2, 3, 4, 5]
        expected_sums = [1, 3, 6, 10, 15]
        
        for num, expected_sum in zip(test_numbers, expected_sums):
            # Create request
            request = SumRequest(number=num)
            
            # Send request
            response = stub.CalculateSum(request)
            
            # Verify response
            assert response.result == expected_sum, f"Expected sum {expected_sum}, got {response.result}"
            logger.info(f"gRPC test: Sent {num}, received sum {response.result}")
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        logger.info("gRPC test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"gRPC test failed: {str(e)}")
        return False

async def test_error_handling():
    """Test error handling for invalid inputs"""
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # Test invalid JSON
            await websocket.send("invalid json")
            response = await websocket.recv()
            response_data = json.loads(response)
            assert "error" in response_data, "Expected error response for invalid JSON"
            
            # Test missing number field
            await websocket.send(json.dumps({"invalid": "data"}))
            response = await websocket.recv()
            response_data = json.loads(response)
            assert "error" in response_data, "Expected error response for missing number field"
            
            # Test non-numeric input
            await websocket.send(json.dumps({"number": "not a number"}))
            response = await websocket.recv()
            response_data = json.loads(response)
            assert "error" in response_data, "Expected error response for non-numeric input"
            
            logger.info("Error handling test completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}")
        return False

async def run_all_tests():
    """Run all system tests"""
    logger.info("Starting system tests...")
    
    # Wait for services to be ready
    logger.info("Waiting for services to be ready...")
    await asyncio.sleep(5)
    
    # Run tests
    tests = [
        ("WebSocket Connection Test", test_websocket_connection),
        ("gRPC Connection Test", test_grpc_connection),
        ("Error Handling Test", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\nRunning {test_name}...")
        result = await test_func()
        results.append((test_name, result))
    
    # Print summary
    logger.info("\nTest Summary:")
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    # Return overall success
    return all(result for _, result in results)

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1) 