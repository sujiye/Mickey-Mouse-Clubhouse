from numpy import False_
from ultralytics import YOLO
import cv2
import yaml
import base64
import time
import asyncio
import websockets
import json

model = YOLO('./src/best.pt')

with open('./room/data.yaml', 'r') as f:
    data = yaml.safe_load(f)
class_names = data['names']

cap = cv2.VideoCapture('./src/test.mp4') # 请替换为您的视频文件路径
# cap = cv2.imread('/Users/sujiye/Downloads/u=1728867338,1613660349&fm=253&app=138&f=JPEG')

async def detect(input_img):
    if not cap.isOpened():
        print("错误：无法打开视频流或摄像头。")
        return

    frame_count = 0
    start_time = time.time()
    fps = 0

    websocket_uri = "ws://127.0.0.1:8765" # WebSocket 服务器地址

    await asyncio.sleep(5) # Add a 5-second delay

    async def receive_messages(websocket):
        try:
            async for message in websocket:
                # 可以在这里处理接收到的消息，例如打印或进一步处理
                # 对于心跳包，websockets库会自动处理pong帧，无需手动干预
                pass
        except websockets.exceptions.ConnectionClosedOK:
            print("WebSocket connection closed normally by server.")
        except Exception as e:
            print(f"Error while receiving messages: {e}")

    async with websockets.connect(websocket_uri, ping_interval=60, ping_timeout=60) as websocket:
        print(f"Connected to {websocket_uri}")
        # 启动一个后台任务来接收消息
        receive_task = asyncio.create_task(receive_messages(websocket))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time > 1: # 每秒更新一次帧率
                fps = frame_count / elapsed_time
                frame_count = 0
                start_time = current_time

            current_timestamp = time.time()

            results = model(frame, device='cuda', verbose=False,show = False)

            this_frame_result = []

            for result in results:
                for box in result.boxes:
                    coords = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    this_frame_result.append({
                        "class": class_names[class_id],
                        "x": x, "y": y, "w": w, "h": h,
                        "confidence": float(confidence)
                    })
                    cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
                    label = f'{class_names[class_id]} {confidence:.2f}'
                    cv2.putText(frame, label, (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # 将帧编码为 JPEG 格式并转换为 Base64 字符串
            _, buffer = cv2.imencode('.jpg', frame)
            encoded_frame = base64.b64encode(buffer).decode('utf-8')

            # 构建要发送的数据包
            data_to_send = {
                "image": encoded_frame,
                "detections": this_frame_result,
                "timestamp": current_timestamp,
                "frame_number": frame_count, # 注意：这里的 frame_count 是从0开始的，且每秒重置
                "fps": fps
            }

            await websocket.send(json.dumps(data_to_send))

            # cv2.imshow('frame', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'): # 将 waitKey(0) 改为 waitKey(1) 以便视频播放
            #     break
        
        # 视频流结束后，取消接收任务
        receive_task.cancel()
        try:
            await receive_task
        except asyncio.CancelledError:
            print("Receive task cancelled.")

    cap.release()
    cv2.destroyAllWindows()

import cProfile
import pstats

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    asyncio.run(detect(0))
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20) # 打印前20个最耗时的函数