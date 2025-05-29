import alibabacloud_oss_v2 as oss
import yaml
from PIL import Image
from io import BytesIO


def load_config():
    with open("../../config.yaml", "r") as f:
        config = yaml.safe_load(f)
        return config


def download(path):
    # 解析命令行参数
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

    # 执行获取对象的请求，指定存储空间名称和对象名称
    result = client.get_object(oss.GetObjectRequest(
        bucket=oss_config["bucket"],  # 指定存储空间名称
        key=path,  # 获取对象名称,  # 指定对象键名
    ))

    # 输出获取对象的结果信息，用于检查请求是否成功
    # print(f'status code: {result.status_code},'
    #       f' request id: {result.request_id},'
    #       f' content length: {result.content_length},'
    #       f' content range: {result.content_range},'
    #       f' content type: {result.content_type},'
    #       f' etag: {result.etag},'
    #       f' last modified: {result.last_modified},'
    #       f' content md5: {result.content_md5},'
    #       f' cache control: {result.cache_control},'
    #       f' content disposition: {result.content_disposition},'
    #       f' content encoding: {result.content_encoding},'
    #       f' expires: {result.expires},'
    #       f' hash crc64: {result.hash_crc64},'
    #       f' storage class: {result.storage_class},'
    #       f' object type: {result.object_type},'
    #       f' version id: {result.version_id},'
    #       f' tagging count: {result.tagging_count},'
    #       f' server side encryption: {result.server_side_encryption},'
    #       f' server side data encryption: {result.server_side_data_encryption},'
    #       f' next append position: {result.next_append_position},'
    #       f' expiration: {result.expiration},'
    #       f' restore: {result.restore},'
    #       f' process status: {result.process_status},'
    #       f' delete marker: {result.delete_marker},'
    # )
    # 读取图像内容为字节流
    image_bytes = result.body.read()

    # 转换为 PIL 图像对象
    image = Image.open(BytesIO(image_bytes))
    return image
