import asyncio
import websockets
import json
import grpc
import sum_pb2
import sum_pb2_grpc
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketProxy:
    def __init__(self):
        # Get configuration from environment variables
        grpc_host = os.getenv('GRPC_HOST', 'localhost')
        grpc_port = os.getenv('GRPC_PORT', '50051')
        self.grpc_channel = grpc.insecure_channel(f'{grpc_host}:{grpc_port}')
        self.sum_stub = sum_pb2_grpc.SumServiceStub(self.grpc_channel)
        logger.info(f"Connected to gRPC server at {grpc_host}:{grpc_port}")

    async def handle_websocket(self, websocket):
        client_id = id(websocket)
        logger.info(f"New WebSocket connection from client {client_id}")
        
        try:
            async for message in websocket:
                try:
                    # Parse the incoming WebSocket message
                    data = json.loads(message)
                    if 'number' not in data:
                        await websocket.send(json.dumps({
                            'error': 'Invalid request. "number" is required.'
                        }))
                        continue

                    number = data['number']
                    logger.info(f"Received number {number} from client {client_id}")

                    # Convert WebSocket message to gRPC request
                    request = sum_pb2.SumRequest(number=number)
                    
                    # Forward request to gRPC server
                    response = self.sum_stub.CalculateSum(request)
                    
                    # Send gRPC response back to WebSocket client
                    await websocket.send(json.dumps({
                        'sum': response.result,
                    }))
                    logger.info(f"Sent response to client {client_id}: {response.result}")

                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}")
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON format'
                    }))
                except grpc.RpcError as e:
                    logger.error(f"gRPC error for client {client_id}: {str(e)}")
                    await websocket.send(json.dumps({
                        'error': f'gRPC error: {str(e)}'
                    }))
                except Exception as e:
                    logger.error(f"Error handling client {client_id}: {str(e)}")
                    await websocket.send(json.dumps({
                        'error': str(e)
                    }))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        finally:
            self.grpc_channel.close()

async def main():
    proxy = WebSocketProxy()
    async with websockets.serve(proxy.handle_websocket, "0.0.0.0", 8765):
        logger.info("WebSocket proxy started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 