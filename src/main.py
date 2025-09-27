import ultralytics
from ultralytics import YOLO

def refer(input_img):
    model = YOLO('yolov8m.pt')
    results = model(source = input_img, show = True, save = True, device = "0" if torch.cuda.is_available() else "cpu", stream = True)

    coordinates = []
    for result in results:
        for box in result.boxes:
            coordinates.append(box.xyxy.tolist())  # Extract bounding box coordinates (x_min, y_min, x_max, y_max)

    return coordinates


def main():
    results = refer(0)
    print(results)

if __name__ == "__main__":
    main()
