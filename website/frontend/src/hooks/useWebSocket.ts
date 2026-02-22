import { useEffect, useRef, useCallback } from 'react';
import { useStore } from '../store';

interface WebSocketMessage {
  type: string;
  analysis_id?: string;
  status?: string;
  data?: any;
  timestamp?: string;
}

export const useWebSocket = (organizationId: string) => {
  const socket = useRef<WebSocket | null>(null);
  const { addUpdate, setConnectionStatus } = useStore();

  const connect = useCallback(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${organizationId}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnectionStatus('connected');
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);

        switch (message.type) {
          case 'analysis_update':
            if (message.analysis_id && message.status) {
              addUpdate({
                id: message.analysis_id,
                status: message.status,
                data: message.data,
                timestamp: message.timestamp
              });
            }
            break;
          // Handle other message types
          default:
            console.log('Unknown message type:', message.type);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(connect, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
    };

    socket.current = ws;

    return () => {
      ws.close();
    };
  }, [organizationId, addUpdate, setConnectionStatus]);

  useEffect(() => {
    const cleanup = connect();
    return () => {
      cleanup();
      if (socket.current) {
        socket.current.close();
      }
    };
  }, [connect]);

  // Return function to send messages
  const sendMessage = useCallback((message: any) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
};