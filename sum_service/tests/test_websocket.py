"""
Tests for the WebSocket server implementation.
"""

import unittest
import asyncio
import websockets
import json
import logging
from src.websocket.server import SumStreamManager, handle_client

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_websocket')

class TestWebSocketServer(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.stream_manager = SumStreamManager()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Clean up the test environment."""
        self.loop.close()

    async def test_client_connection(self):
        """Test client connection and registration."""
        # Create a mock WebSocket
        mock_ws = unittest.mock.AsyncMock()
        
        # Register the client
        await self.stream_manager.register(mock_ws)
        
        # Verify the client was registered
        self.assertIn(mock_ws, self.stream_manager.clients)
        
        # Verify the initial sum was sent
        mock_ws.send.assert_called_once()
        message = json.loads(mock_ws.send.call_args[0][0])
        self.assertEqual(message["type"], "sum_update")
        self.assertEqual(message["value"], 0)

    async def test_broadcast_sum(self):
        """Test broadcasting sum updates to all clients."""
        # Create mock WebSocket clients
        mock_ws1 = unittest.mock.AsyncMock()
        mock_ws2 = unittest.mock.AsyncMock()
        
        # Register clients
        await self.stream_manager.register(mock_ws1)
        await self.stream_manager.register(mock_ws2)
        
        # Broadcast a new sum
        await self.stream_manager.broadcast_sum(42)
        
        # Verify both clients received the update
        for mock_ws in [mock_ws1, mock_ws2]:
            mock_ws.send.assert_called()
            message = json.loads(mock_ws.send.call_args[0][0])
            self.assertEqual(message["type"], "sum_update")
            self.assertEqual(message["value"], 42)

    def test_add_number(self):
        """Test adding a number through gRPC."""
        # Add a number
        future = self.stream_manager.add_number(10)
        result = future.result()
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result, 10)  # First number should be the same as the input

if __name__ == '__main__':
    unittest.main() 