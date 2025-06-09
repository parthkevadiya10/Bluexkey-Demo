import asyncio
import websockets
import json
import grpc
import sum_pb2
import sum_pb2_grpc

class WebSocketServer:
    def __init__(self, grpc_host='grpc-server', grpc_port=50051):
        self.grpc_channel = grpc.insecure_channel(f'{grpc_host}:{grpc_port}')
        self.sum_stub = sum_pb2_grpc.SumServiceStub(self.grpc_channel)
        self.number_buffer = {}  # Store numbers for each client

    async def handle_websocket(self, websocket):
        client_id = id(websocket)
        self.number_buffer[client_id] = []
        
        try:
            async for message in websocket:
                try:
                    # Parse the incoming message
                    data = json.loads(message)
                    if 'number' not in data:
                        await websocket.send(json.dumps({
                            'error': 'Invalid request. "number" is required.'
                        }))
                        continue

                    number = data['number']
                    self.number_buffer[client_id].append(number)

                    # If we have two numbers, calculate the sum
                    if len(self.number_buffer[client_id]) == 2:
                        a, b = self.number_buffer[client_id]
                        # Call gRPC service
                        request = sum_pb2.SumRequest(number=a)
                        response = self.sum_stub.CalculateSum(request)
                        request = sum_pb2.SumRequest(number=b)
                        response = self.sum_stub.CalculateSum(request)

                        # Send response back to WebSocket client
                        await websocket.send(json.dumps({
                            'result': response.result,
                            'numbers': [a, b]
                        }))
                        
                        # Clear the buffer for this client
                        self.number_buffer[client_id] = []
                    else:
                        # Send acknowledgment for the first number
                        await websocket.send(json.dumps({
                            'message': f'Received number {number}. Waiting for second number...'
                        }))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON format'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'error': str(e)
                    }))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Clean up the buffer when client disconnects
            if client_id in self.number_buffer:
                del self.number_buffer[client_id]
            self.grpc_channel.close()

async def main():
    server = WebSocketServer()
    async with websockets.serve(server.handle_websocket, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 