import grpc
from concurrent import futures
import sum_pb2
import sum_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SumServicer(sum_pb2_grpc.SumServiceServicer):
    def __init__(self):
        self.running_sum = 0

    def CalculateSum(self, request, context):
        # Add the new number to running sum
        self.running_sum += request.number
        logger.info(f"Received number {request.number}, new sum: {self.running_sum}")
        return sum_pb2.SumResponse(result=self.running_sum)

class HealthServicer(health_pb2_grpc.HealthServicer):
    def __init__(self):
        self._server_status = health_pb2.HealthCheckResponse.SERVING

    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(status=self._server_status)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add SumService
    sum_pb2_grpc.add_SumServiceServicer_to_server(SumServicer(), server)
    
    # Add health service
    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    
    # Add reflection service
    SERVICE_NAMES = (
        sum_pb2.DESCRIPTOR.services_by_name['SumService'].full_name,
        health_pb2.DESCRIPTOR.services_by_name['Health'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Start server
    port = 50051
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"gRPC server started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 