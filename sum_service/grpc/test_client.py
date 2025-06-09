import grpc
import sum_pb2
import sum_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

def test_sum_service():
    # Create a channel to the server using the Docker service name
    with grpc.insecure_channel('grpc-server:50051') as channel:
        # Create a stub (client)
        stub = sum_pb2_grpc.SumServiceStub(channel)
        
        # Test sending first number
        first_request = sum_pb2.SumRequest(number=5)
        first_response = stub.CalculateSum(first_request)
        print(f"First number sent: 5")
        print(f"Response (waiting for second number): {first_response.result}")
        
        # Test sending second number
        second_request = sum_pb2.SumRequest(number=3)
        second_response = stub.CalculateSum(second_request)
        print(f"\nSecond number sent: 3")
        print(f"Final sum: {second_response.result}")

def test_health_check():
    # Create a channel to the server using the Docker service name
    with grpc.insecure_channel('grpc-server:50051') as channel:
        # Create a health check stub
        health_stub = health_pb2_grpc.HealthStub(channel)
        
        # Check the health status
        request = health_pb2.HealthCheckRequest()
        response = health_stub.Check(request)
        print(f"\nHealth check status: {response.status}")

if __name__ == '__main__':
    print("Testing Sum Service...")
    test_sum_service()
    
    print("\nTesting Health Check...")
    test_health_check() 