from service.oss.upload_storage import upload
from service.oss.download_storage import download
from ultralytics import YOLO
from datetime import datetime
from rabbitmq.publish import push_message

dicts = {
    0: "missing_hole",
    1: "mouse_bite",
    2: "open_circuit",
    3: "short",
    4: "spur",
    5: "spurious_copper"
}


def save_image(data, image_name):
    # 获取对应类别索引，并获取对应数量
    data_names = [data.names[int(cls.item())] for cls in data.boxes.cls]
    data_count = {}
    for name in data_names:
        data_count[name] = data_count.get(name, 0) + 1

    data_content = ""  # 记录缺陷内容
    data_level = 0  # 统计缺陷等级
    for k, v in data_count.items():
        data_content += f"{v} {k + ('s' if v > 1 else '')}, "
        if v > 0:
            data_level += 1 << list(dicts.values()).index(k)

    data_image = data.plot()  # 拿到标记后的图像
    data_image_path = upload(data_image, image_name)
    half_data = {
        "data_content": data_content,
        "data_image_path": data_image_path,
        "data_level": data_level
    }
    return half_data


def model_work(front_path, back_path):
    # 从OSS拿到图片
    front_image = download(front_path)
    back_image = download(back_path)
    print("图片下载成功")

    # 导入训练好的模型
    model = YOLO('../model/ModelDetectionPCB.pt')

    # 拿到模型预测的数据
    front_results = model.predict(front_image, save=False)
    back_results = model.predict(back_image, save=False)
    fr = front_results[0]
    br = back_results[0]

    # 保存图片并返回图片路径和缺陷等级
    fr_data = save_image(fr, front_path.split('/')[-1])
    br_data = save_image(br, back_path.split('/')[-1])
    total_data = {
        "content":  fr_data["data_content"] + br_data["data_content"],
        "frontImage": fr_data["data_image_path"],
        "backImage": br_data["data_image_path"],
        "defectLevel": fr_data["data_level"] + br_data["data_level"] * 1000
    }
    return total_data


def service(json):
    serial_number = json['serialNumber']
    front_image_path = json['frontImage']
    back_image_path = json['backImage']
    save_data = model_work(front_image_path, back_image_path)
    push_data = {
        "serialNumber": serial_number,
        "content": save_data["content"],
        "frontDefectImg": save_data["frontImage"],
        "backDefectImg": save_data["backImage"],
        "defectLevel": save_data["defectLevel"],
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    push_message(push_data)

