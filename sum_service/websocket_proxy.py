import asyncio
import json
import logging
import grpc
from websockets.server import serve
from sum_service.grpc import sum_pb2, sum_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebSocketProxy:
    def __init__(self, grpc_host, grpc_port):
        self.grpc_host = grpc_host
        self.grpc_port = grpc_port
        self.channel = None
        self.stub = None
        self.connect_grpc()

    def connect_grpc(self):
        """Connect to gRPC server with retry logic"""
        try:
            if self.channel:
                self.channel.close()
            
            # Create a new channel with keepalive settings
            self.channel = grpc.aio.insecure_channel(
                f'{self.grpc_host}:{self.grpc_port}',
                options=[
                    ('grpc.keepalive_time_ms', 30000),  # Send keepalive ping every 30 seconds
                    ('grpc.keepalive_timeout_ms', 10000),  # Wait 10 seconds for keepalive ping ack
                    ('grpc.keepalive_permit_without_calls', True),  # Allow keepalive pings when there are no calls
                    ('grpc.http2.max_pings_without_data', 0),  # Allow unlimited pings without data
                    ('grpc.http2.min_time_between_pings_ms', 10000),  # Minimum time between pings
                ]
            )
            self.stub = sum_pb2_grpc.SumStub(self.channel)
            logger.info(f"Connected to gRPC server at {self.grpc_host}:{self.grpc_port}")
        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            raise

    async def handle_client(self, websocket):
        """Handle WebSocket client connection"""
        client_id = id(websocket)
        logger.info(f"New WebSocket connection from client {client_id}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if 'number' not in data:
                        await websocket.send(json.dumps({"error": "Missing 'number' field"}))
                        continue

                    number = data['number']
                    logger.info(f"Received number {number} from client {client_id}")

                    try:
                        # Create request and get response
                        request = sum_pb2.NumberRequest(number=number)
                        response = await self.stub.AddNumber(request)
                        
                        # Send response back to client
                        result = {"result": response.sum}
                        await websocket.send(json.dumps(result))
                        logger.info(f"Sent response to client {client_id}: {response.sum}")
                    except grpc.RpcError as e:
                        if e.code() == grpc.StatusCode.UNAVAILABLE:
                            logger.warning("gRPC connection lost, attempting to reconnect...")
                            self.connect_grpc()
                            # Retry the request after reconnection
                            request = sum_pb2.NumberRequest(number=number)
                            response = await self.stub.AddNumber(request)
                            result = {"result": response.sum}
                            await websocket.send(json.dumps(result))
                            logger.info(f"Sent response to client {client_id} after reconnection: {response.sum}")
                        else:
                            raise

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON format"}))
                except Exception as e:
                    logger.error(f"Error handling client {client_id}: {e}")
                    await websocket.send(json.dumps({"error": str(e)}))

        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            logger.info(f"Client {client_id} disconnected")

async def main():
    # Get configuration from environment variables
    grpc_host = "grpc-server"
    grpc_port = 50051
    websocket_host = "0.0.0.0"
    websocket_port = 8765

    # Create WebSocket proxy instance
    proxy = WebSocketProxy(grpc_host, grpc_port)

    # Start WebSocket server
    async with serve(proxy.handle_client, websocket_host, websocket_port):
        logger.info(f"WebSocket proxy started on ws://{websocket_host}:{websocket_port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 