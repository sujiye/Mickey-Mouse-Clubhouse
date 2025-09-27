from ultralytics import YOLO

def main():
    proto_model = YOLO('yolov8m.pt')

    proto_model.train(
        data ='data.yaml',
        epochs=200,
        imgsz=640,
        batch=16,
        device= '0',
    )

    print ("Training completed successfully.")

if __name__ == "__main__":
    main()