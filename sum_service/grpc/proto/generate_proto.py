import os
import subprocess

def generate_proto():
    proto_dir = os.path.dirname(os.path.abspath(__file__))
    proto_file = os.path.join(proto_dir, 'sum.proto')
    
    # Generate Python gRPC files
    subprocess.run([
        'python', '-m', 'grpc_tools.protoc',
        f'--proto_path={proto_dir}',
        f'--python_out={proto_dir}',
        f'--grpc_python_out={proto_dir}',
        proto_file
    ])

if __name__ == '__main__':
    generate_proto() 