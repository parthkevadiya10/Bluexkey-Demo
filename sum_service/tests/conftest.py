import os
import sys
import pytest
import grpc
from concurrent import futures
from grpc_health.v1 import health_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_reflection.v1alpha import reflection

# Add the proto directory to Python path
proto_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'grpc', 'proto')
sys.path.append(proto_dir)

def ensure_proto_files():
    """Ensure proto files are generated"""
    try:
        import grpc_tools.protoc
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "grpcio-tools"])
        import grpc_tools.protoc

    # Generate proto files
    import subprocess
    subprocess.run([
        sys.executable, '-m', 'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        os.path.join(proto_dir, 'sum.proto')
    ])

# Generate proto files first
ensure_proto_files()

# Now import the generated files
from sum_pb2 import SumRequest, SumResponse
from sum_pb2_grpc import SumServiceStub, SumServiceServicer
from sum_service.grpc.server import SumServicer, HealthServicer

@pytest.fixture(scope="session")
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SumServiceServicer.add_SumServiceServicer_to_server(SumServicer(), server)
    health_pb2_grpc.add_HealthServicer_to_server(HealthServicer(), server)
    port = server.add_insecure_port('[::]:0')
    server.start()
    yield server, port
    server.stop(0)

@pytest.fixture(scope="session")
def grpc_channel():
    """Create a gRPC channel for testing"""
    channel = grpc.insecure_channel('localhost:50051')
    yield channel
    channel.close() 