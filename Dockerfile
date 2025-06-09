FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install grpc_health_probe
RUN GRPC_HEALTH_PROBE_VERSION=v0.4.11 && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-amd64 && \
    chmod +x /bin/grpc_health_probe

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Clean up any existing generated files and regenerate gRPC code
RUN rm -f sum_pb2.py sum_pb2_grpc.py && \
    python -m grpc_tools.protoc -I./sum_service/grpc/proto --python_out=. --grpc_python_out=. ./sum_service/grpc/proto/sum.proto

# Install the package in development mode
RUN pip install -e .

# Set Python path
ENV PYTHONPATH=/app

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Default command (can be overridden by docker-compose)
CMD ["python", "-m", "sum_service.grpc.server"] 