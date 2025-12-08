import torch
import coremltools as ct
import os

# 假设您的YOLO模型文件名为 'best.pt'
model_path = 'best.pt'
output_mlmodel_name = 'furniture_detect.mlmodel' # 您可以自定义输出文件名

if not os.path.exists(model_path):
    print(f"错误：未找到模型文件 '{model_path}'。请确保 'best.pt' 文件与此脚本在同一目录下。")
else:
    print(f"正在加载 PyTorch 模型：{model_path}")
    try:
        # 尝试加载YOLOv5或YOLOv8模型
        # 对于YOLOv5，通常是 model = torch.load(model_path)['model'].float().eval()
        # 对于YOLOv8，可以使用 ultralytics 库的 YOLO 类
        
        # 尝试使用ultralytics加载，如果失败则尝试通用torch加载
        try:
            from ultralytics import YOLO
            model = YOLO(model_path).model.float().eval()
            print("使用 ultralytics 库成功加载模型。")
        except ImportError:
            print("未安装 ultralytics 库，尝试使用通用 torch.load 加载。")
            model = torch.load(model_path)['model'].float().eval()
            print("使用通用 torch.load 成功加载模型。")

        # 示例输入，用于确定Core ML模型的输入形状
        # YOLOv5/v8通常是(1, 3, 640, 640)
        example_input = torch.rand(1, 3, 640, 640)

        # 将模型转换为Core ML格式
        # 注意：YOLO模型的输出通常需要后处理。这里的输出形状是一个示例，
        # 您可能需要根据您的模型版本和训练配置进行调整。
        # 例如，YOLOv5 640x640 80类模型的输出形状可能是 (1, 25200, 85)
        # 其中 25200 是检测框的数量，85 = 4 (bbox) + 1 (confidence) + 80 (classes)
        
        # 追踪模型以获取Core ML兼容的表示
        traced_model = torch.jit.trace(model, example_input)

        mlmodel = ct.convert(
            traced_model,
            inputs=[ct.ImageType(name="image", shape=example_input.shape, scale=1/255.0, bias=[0, 0, 0])],
            outputs=[ct.FeatureTypes.multiArray(name="output", shape=(1, 25200, 85))], # 请根据您的模型实际输出调整
            minimum_deployment_target=ct.target.iOS15 # 根据您的应用支持的最低iOS版本调整
        )

        # 保存Core ML模型
        mlmodel.save(output_mlmodel_name)
        print(f"模型已成功转换为 {output_mlmodel_name}")

    except Exception as e:
        print(f"模型转换过程中发生错误：{e}")
        print("请检查您的模型路径、输入形状和输出形状是否正确。")
        print("如果模型是YOLOv8，请确保安装了'ultralytics'库。")
        print("如果仍然遇到问题，您可能需要查阅您的YOLO模型版本的官方文档，了解如何将其转换为Core ML。")
