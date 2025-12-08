import asyncio
import websockets
import json

CONNECTED_CLIENTS = set()

async def handler(websocket):
    print(f"Client connected: {websocket.remote_address}")
    CONNECTED_CLIENTS.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message from {websocket.remote_address}: {message[:50]}...") # Log first 50 chars of message
            for client in CONNECTED_CLIENTS:
                if client != websocket:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Client {websocket.remote_address} disconnected normally.")
    except Exception as e:
        print(f"WebSocket error with {websocket.remote_address}: {e}")
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        print(f"Client {websocket.remote_address} removed from active connections.")

async def main():
    # 启动 WebSocket 服务器，监听所有可用网络接口的 8765 端口
    async with websockets.serve(handler, "0.0.0.0", 8765, ping_interval=60, ping_timeout=60):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())