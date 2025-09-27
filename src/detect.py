from ultralytics import YOLO
import cv2

model = YOLO('best.pt')
cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('./test.mp4')

def detect(input_img):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)

        this_frame_result = []

        for result in results:
            for box in result.boxes:
                cv2.rectangle(frame, (int(box.xyxy[0]), int(box.xyxy[1])), (int(box.xyxy[2]), int(box.xyxy[3])), (0, 255, 0), 2)
                for i, box in enumerate(zip(boxes.data)):
                    x1, y1, x2, y2 = box[:4].cpu().numpy().astype(int)
                    confidence = box[4].cpu().numpy()
                    class_id = int(box[5].cpu().numpy())
                    this_frame_result.append([class_id, x1, y1, x2, y2, confidence])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f'{class_names[class_id]} {confidence:.2f}'
                    cv2.putText(frame, label, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        if not this_frame_result == []:
            print(this_frame_result)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        return this_frame_result

if __name__ == '__main__':
    detect(0)