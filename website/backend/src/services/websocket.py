"""WebSocket service for real-time updates."""
from fastapi import WebSocket
from typing import Dict, Set, Optional
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Manage WebSocket connections."""
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.last_messages: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, organization_id: str):
        """Connect a new client."""
        await websocket.accept()
        if organization_id not in self.active_connections:
            self.active_connections[organization_id] = set()
        self.active_connections[organization_id].add(websocket)

        # Send last message if available
        if organization_id in self.last_messages:
            await websocket.send_json(self.last_messages[organization_id])

    def disconnect(self, websocket: WebSocket, organization_id: str):
        """Disconnect a client."""
        self.active_connections[organization_id].remove(websocket)
        if not self.active_connections[organization_id]:
            del self.active_connections[organization_id]

    async def broadcast_to_organization(self, organization_id: str, message: dict):
        """Broadcast message to all connections in an organization."""
        if organization_id not in self.active_connections:
            return

        # Store last message
        self.last_messages[organization_id] = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Broadcast to all connections
        for connection in self.active_connections[organization_id]:
            try:
                await connection.send_json(self.last_messages[organization_id])
            except:
                await self.disconnect(connection, organization_id)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket, organization_id: str):
    """Handle WebSocket connection."""
    await manager.connect(websocket, organization_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except:
        manager.disconnect(websocket, organization_id)

async def send_analysis_update(organization_id: str, analysis_id: str, status: str, data: Optional[dict] = None):
    """Send analysis update to organization."""
    message = {
        "type": "analysis_update",
        "analysis_id": analysis_id,
        "status": status,
        "data": data
    }
    await manager.broadcast_to_organization(organization_id, message)