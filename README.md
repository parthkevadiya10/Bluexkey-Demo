# gRPC-WebSocket Demo

This demo project demonstrates a microservice architecture using gRPC, WebSocket, and Envoy proxy. It implements a simple running sum service that can be accessed through both gRPC and WebSocket interfaces.

## Architecture

- **gRPC Server**: Handles the core business logic for calculating running sums
- **WebSocket Proxy**: Bridges WebSocket clients to the gRPC server
- **Envoy Proxy**: Handles gRPC-Web protocol translation

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- pip

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd demo
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

## Running the Services

Start all services using Docker Compose:
```bash
docker-compose up -d
```

## Testing

1. Run the system tests:
```bash
pytest test_system.py -v
```

2. Test the WebSocket client:
```bash
python test_websocket_client.py
```

## Project Structure

```
.
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile           # Docker build instructions
├── envoy.yaml          # Envoy proxy configuration
├── requirements.txt    # Python dependencies
├── setup.py           # Package setup
├── sum_service/       # Main service package
│   ├── grpc/         # gRPC service implementation
│   ├── tests/        # Test cases
│   └── websocket_proxy.py  # WebSocket proxy
├── test_system.py     # System integration tests
└── test_websocket_client.py  # WebSocket client test
```

## API

### WebSocket API

Connect to `ws://localhost:8765` and send JSON messages in the format:
```json
{"number": 5}
```

Response format:
```json
{"sum": 15}
```

### gRPC API

The gRPC service is available at `localhost:50051` with the following methods:
- `AddNumber`: Add a number to the running sum
- `GetSum`: Get the current sum
- `ResetSum`: Reset the sum to zero

## License

MIT 