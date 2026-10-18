"""WebSocket connection manager for real-time updates"""

from fastapi import WebSocket
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time data streaming"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_watchlists: Dict[WebSocket, List[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept and register new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.user_watchlists:
            del self.user_watchlists[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")

    def set_watchlist(self, websocket: WebSocket, symbols: List[str]):
        """Set watchlist for a connection"""
        self.user_watchlists[websocket] = symbols

    def get_watchlist(self, websocket: WebSocket) -> List[str]:
        """Get watchlist for a connection"""
        return self.user_watchlists.get(websocket, [])
