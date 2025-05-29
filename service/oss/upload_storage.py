import alibabacloud_oss_v2 as oss
import yaml
from datetime import datetime
import cv2


def load_config():
    with open("../config.yaml", "r", encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return config


def upload(upload_data, file_name):
    oss_config = load_config()
    oss_config = oss_config["oss"]

    # 从环境变量中加载凭证信息，用于身份验证
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    # 设置配置中的区域信息
    cfg.region = oss_config["region"]
    # 如果提供了endpoint参数，则设置配置中的endpoint
    if oss_config.get("endpoint"):
        cfg.endpoint = oss_config["endpoint"]

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 定义要上传的数据内容
    _, img_encoded = cv2.imencode('.jpg', upload_data)
    data = img_encoded.tobytes()

    # 获取当前日期并格式化
    now = datetime.now()
    year = str(now.year)
    month = f"{now.month:02d}"  # 补零，如 5 → "05"
    day = f"{now.day:02d}"

    object_key = f"{oss_config.get('key_prefix', '') + year + '/' + month + '/' + day + '/'}{file_name}"
    print("开始上传文件")

    # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
    result = client.put_object(oss.PutObjectRequest(
        bucket=oss_config["bucket"],
        key=object_key,
        body=data,
    ))

    # 输出请求的结果状态码、请求ID、内容MD5、ETag、CRC64校验码和版本ID，用于检查请求是否成功
    # print(f'status code: {result.status_code},'
    #       f' request id: {result.request_id},'
    #       f' content md5: {result.content_md5},'
    #       f' etag: {result.etag},'
    #       f' hash crc64: {result.hash_crc64},'
    #       f' version id: {result.version_id},'
    # )

    if 200 <= result.status_code < 300:
        # 手动拼接文件访问 URL
        endpoint = oss_config["endpoint"]
        bucket = oss_config["bucket"]
        file_url = f"https://{bucket}.oss-{oss_config['region']}.aliyuncs.com{endpoint}/{object_key}"
        print(f"文件上传成功. URL: {file_url}")
        return file_url  # 返回完整路径
    else:
        print(f"Upload failed. Status code: {result.status_code}")
        return None
