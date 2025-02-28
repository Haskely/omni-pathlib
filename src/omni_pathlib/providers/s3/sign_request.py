import hashlib
import hmac
import urllib.parse
from datetime import datetime, timezone


def sign_request(
    method: str,
    host: str,
    region: str,
    access_key: str,
    secret_key: str,
    uri: str = "/",
    query_params: dict | None = None,
    headers: dict | None = None,
    payload: bytes | None = None,
) -> dict:
    """
    为 S3 请求生成 AWS Signature V4 签名
    支持 signed 和 unsigned payload

    Args:
        method: HTTP 方法 (GET, PUT 等)
        host: S3 endpoint 主机名
        region: AWS 区域
        access_key: AWS access key
        secret_key: AWS secret key
        uri: 请求路径
        query_params: 查询参数字典
        headers: 请求头字典
        payload: 请求体字节数据,如果为 None 则使用 unsigned payload

    Returns:
        包含签名和认证头的字典
    """
    # 设置基本变量
    algorithm = "AWS4-HMAC-SHA256"
    service = "s3"
    now = datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    # 准备规范请求
    canonical_uri = urllib.parse.quote(uri, safe="/")
    canonical_querystring = ""
    if query_params:
        # 严格按照字典序排序
        canonical_querystring = "&".join(
            [
                f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
                for k, v in sorted(query_params.items())
            ]
        )

    # 准备请求头
    if headers is None:
        headers = {}
    headers["host"] = host
    headers["x-amz-date"] = amz_date

    # 计算 payload hash
    if payload is None:
        payload_hash = "UNSIGNED-PAYLOAD"
    else:
        payload_hash = hashlib.sha256(payload).hexdigest()

    headers["x-amz-content-sha256"] = payload_hash  # 使用计算出的 payload hash

    # 创建规范头部字符串
    canonical_headers = "".join(
        [f"{k.lower()}:{v}\n" for k, v in sorted(headers.items())]
    )
    signed_headers = ";".join([k.lower() for k in sorted(headers.keys())])

    # 组合规范请求
    canonical_request = (
        f"{method}\n{canonical_uri}\n{canonical_querystring}\n"
        f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )

    # 创建签名字符串
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        f"{algorithm}\n{amz_date}\n{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
    )

    # 计算签名
    k_date = hmac.new(f"AWS4{secret_key}".encode(), date_stamp.encode(), hashlib.sha256)
    k_region = hmac.new(k_date.digest(), region.encode(), hashlib.sha256)
    k_service = hmac.new(k_region.digest(), service.encode(), hashlib.sha256)
    k_signing = hmac.new(k_service.digest(), b"aws4_request", hashlib.sha256)
    signature = hmac.new(
        k_signing.digest(), string_to_sign.encode(), hashlib.sha256
    ).hexdigest()

    # 构造授权头
    authorization_header = (
        f"{algorithm} Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    # 更新头部
    headers["Authorization"] = authorization_header

    return {
        "headers": headers,
        "canonical_querystring": canonical_querystring,
        "signed_url": f"{canonical_uri}{'?' + canonical_querystring if canonical_querystring else ''}",
    }
