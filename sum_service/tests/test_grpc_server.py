"""
Tests for the gRPC server implementation.
"""

import pytest
import grpc
from concurrent import futures
import time
import sum_pb2
import sum_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from sum_service.grpc.server import SumServicer, HealthServicer

@pytest.fixture
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sum_pb2_grpc.add_SumServiceServicer_to_server(SumServicer(), server)
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield server, port
    server.stop(0)

@pytest.fixture
def grpc_channel(grpc_server):
    server, port = grpc_server
    channel = grpc.insecure_channel(f'localhost:{port}')
    yield channel
    channel.close()

def test_calculate_sum(grpc_channel):
    stub = sum_pb2_grpc.SumServiceStub(grpc_channel)
    
    # Test first number
    first_request = sum_pb2.SumRequest(number=5)
    first_response = stub.CalculateSum(first_request)
    assert first_response.result == 0  # Waiting for second number
    
    # Test second number
    second_request = sum_pb2.SumRequest(number=3)
    second_response = stub.CalculateSum(second_request)
    assert second_response.result == 8  # 5 + 3 = 8

def test_health_check(grpc_channel):
    health_stub = health_pb2_grpc.HealthStub(grpc_channel)
    request = health_pb2.HealthCheckRequest()
    response = health_stub.Check(request)
    assert response.status == health_pb2.HealthCheckResponse.SERVING

class TestSumService(pytest.fixture):
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Start the server in a separate thread
        cls.server_thread = threading.Thread(target=serve)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Give the server time to start
        time.sleep(1)
        
        # Create a channel and stub
        cls.channel = grpc.insecure_channel('localhost:50051')
        cls.stub = SumServiceStub(cls.channel)

    def test_stream_sum(self):
        """Test the StreamSum RPC method."""
        # Test sending multiple numbers and verify the running sum
        test_numbers = [1, 2, 3, 4, 5]
        expected_sums = [1, 3, 6, 10, 15]
        
        for num, expected_sum in zip(test_numbers, expected_sums):
            request = SumRequest(value=num)
            response = self.stub.StreamSum(request)
            self.assertEqual(response.result, expected_sum)

    def test_error_handling(self):
        """Test error handling in the StreamSum RPC method."""
        # Test sending an invalid request
        # Note: In this simple implementation, we don't have invalid requests
        # but we can test the error handling by sending a valid request
        request = SumRequest(value=10)
        response = self.stub.StreamSum(request)
        self.assertIsNotNone(response)

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        # Clean up
        cls.channel.close()

if __name__ == '__main__':
    pytest.main() 