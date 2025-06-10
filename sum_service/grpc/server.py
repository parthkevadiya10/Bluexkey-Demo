import grpc
from concurrent import futures
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
import logging
import os
import sys
import socket
import time

# Add proto directory to Python path
proto_dir = os.path.join(os.path.dirname(__file__), 'proto')
sys.path.append(proto_dir)

# Import generated proto files
from sum_pb2 import SumRequest, SumResponse
from sum_pb2_grpc import SumServiceServicer, add_SumServiceServicer_to_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SumServicer(SumServiceServicer):
    def __init__(self):
        self.running_sum = 0

    def CalculateSum(self, request, context):
        # Add the new number to running sum
        self.running_sum += request.number
        logger.info(f"Received number {request.number}, new sum: {self.running_sum}")
        return SumResponse(result=self.running_sum)

    def ResetSum(self, request, context):
        # Reset the running sum to 0
        self.running_sum = 0
        logger.info("Reset running sum to 0")
        return SumResponse(result=0)

class HealthServicer(health_pb2_grpc.HealthServicer):
    def __init__(self):
        self._server_status = health_pb2.HealthCheckResponse.SERVING

    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(status=self._server_status)

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Add SumService
        add_SumServiceServicer_to_server(SumServicer(), server)
        
        # Add health service
        health_servicer = HealthServicer()
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
        
        # Add reflection service
        SERVICE_NAMES = (
            'sum.SumService',
            health_pb2.DESCRIPTOR.services_by_name['Health'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
        
        # Find an available port
        port = find_available_port(50051)
        logger.info(f"Found available port: {port}")
        
        # Try different binding approaches
        binding_attempts = [
            f'0.0.0.0:{port}',
            f'127.0.0.1:{port}',
            f'localhost:{port}'
        ]
        
        bound = False
        for binding in binding_attempts:
            try:
                server.add_insecure_port(binding)
                logger.info(f"Successfully bound to {binding}")
                bound = True
                break
            except Exception as e:
                logger.warning(f"Failed to bind to {binding}: {str(e)}")
                time.sleep(1)  # Wait a bit before trying the next binding
        
        if not bound:
            raise RuntimeError("Failed to bind to any address")
        
        server.start()
        logger.info(f"gRPC server started on port {port}")
        
        # Keep the server running
        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server terminated unexpectedly: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {str(e)}")
        raise

if __name__ == '__main__':
    serve() 