import asyncio
import websockets

async def listen_to_websocket():
    uri = "ws://10.21.220.164:8765"
    print(f"尝试连接到 {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print(f"成功连接到 {uri}。开始监听消息...")
            while True:
                message = await websocket.recv()
                print(f"收到消息: {message}")
    except Exception as e:
        print(f"连接或接收消息时发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(listen_to_websocket())
