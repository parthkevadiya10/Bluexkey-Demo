import pytest
import grpc
from concurrent import futures
import sum_pb2_grpc
from grpc_health.v1 import health_pb2_grpc
from sum_service.grpc.server import SumServicer, HealthServicer

@pytest.fixture(scope="session")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sum_pb2_grpc.add_SumServiceServicer_to_server(SumServicer(), server)
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield server, port
    server.stop(0)

@pytest.fixture(scope="session")
def grpc_channel(grpc_server):
    server, port = grpc_server
    channel = grpc.insecure_channel(f'localhost:{port}')
    yield channel
    channel.close() 