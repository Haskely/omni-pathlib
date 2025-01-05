import os
import aiohttp
import hashlib
import hmac
import datetime
from urllib.parse import quote
import asyncio

class S3Client:
    def __init__(self, access_key, secret_key, endpoint_url):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url.rstrip('/')
        
    def _generate_signature(self, method: str, bucket: str, key: str, date: str| None = None, payload_hash: str| None = None) -> tuple[dict, str]:
        """生成S3请求所需的签名和认证头信息
        
        Args:
            method: HTTP方法 (GET, PUT, DELETE等)
            bucket: S3存储桶名称
            key: 对象键名
            date: 可选的时间戳，如果不提供则使用当前时间
            payload_hash: 请求体的SHA256哈希值
            
        Returns:
            tuple: (headers字典, 完整URL)
        """
        if not date:
            date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        if not payload_hash:
            payload_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # 空内容的哈希值
        
        datestamp = date[:8]
        
        url = f"{self.endpoint_url}/{bucket}/{key}"
        
        endpoint_host = self.endpoint_url.replace('http://', '').replace('https://', '')
        canonical_headers = f"host:{endpoint_host}\nx-amz-date:{date}"
        signed_headers = "host;x-amz-date"
        
        canonical_request = (
            f"{method}\n"
            f"/{bucket}/{key}\n"
            f"\n"
            f"{canonical_headers}\n"
            f"\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )
        
        credential_scope = f"{datestamp}/us-east-1/s3/aws4_request"
        string_to_sign = (
            f"AWS4-HMAC-SHA256\n"
            f"{date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )
        
        k_date = hmac.new(f"AWS4{self.secret_key}".encode('utf-8'), datestamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, b"us-east-1", hashlib.sha256).digest()
        k_service = hmac.new(k_region, b"s3", hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        auth_header = (
            f"AWS4-HMAC-SHA256 "
            f"Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        headers = {
            "Authorization": auth_header,
            "x-amz-date": date,
            "x-amz-content-sha256": payload_hash
        }
        
        return headers, url

    async def download_file(self, bucket: str, key: str, output_path: str):
        headers, url = self._generate_signature("GET", bucket, key)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    with open(output_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    return True
                else:
                    raise Exception(f"下载失败: {response.status} {await response.text()}")

    def _get_signing_key(self, date_stamp: str) -> bytes:
        """获取签名密钥"""
        k_date = hmac.new(f"AWS4{self.secret_key}".encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, b"us-east-1", hashlib.sha256).digest()
        k_service = hmac.new(k_region, b"s3", hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
        return k_signing

    async def upload_file(self, bucket: str, key: str, file_path: str, chunk_size: int = 65536):
        """使用分块上传方式上传文件到S3"""
        file_size = os.path.getsize(file_path)
        date = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        date_stamp = date[:8]
        
        # 生成初始请求的headers和签名密钥
        headers, url = self._generate_signature(
            "PUT", 
            bucket, 
            key,
            date=date,
            payload_hash="STREAMING-AWS4-HMAC-SHA256-PAYLOAD"
        )
        headers.update({
            'Content-Encoding': 'aws-chunked',
            'Content-Type': 'application/octet-stream',
            'x-amz-decoded-content-length': str(file_size)
        })

        # 获取签名密钥
        signing_key = self._get_signing_key(date_stamp)
        
        # 保存种子签名，用于第一个数据块的签名计算
        seed_signature = headers['Authorization'].split('Signature=')[1]

        async def chunk_generator(file_path):
            previous_signature = seed_signature
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        # 计算最后一个空块的签名
                        final_signature = self._calculate_chunk_signature(
                            b"", 
                            previous_signature, 
                            date, 
                            signing_key
                        )
                        yield f"0;chunk-signature={final_signature}\r\n\r\n".encode('utf-8')
                        break
                    
                    # 计算当前块的签名
                    chunk_signature = self._calculate_chunk_signature(
                        chunk,
                        previous_signature,
                        date,
                        signing_key
                    )
                    
                    # 更新前一个签名
                    previous_signature = chunk_signature
                    
                    # 构造分块格式
                    chunk_header = f"{hex(len(chunk))[2:]};chunk-signature={chunk_signature}\r\n"
                    yield chunk_header.encode('utf-8')
                    yield chunk
                    yield b"\r\n"

        # 使用分块上传
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, data=chunk_generator(file_path)) as response:
                if response.status in (200, 201):
                    return True
                else:
                    raise Exception(f"上传失败: {response.status} {await response.text()}")

    def _calculate_chunk_signature(self, chunk_data: bytes, previous_signature: str, date: str, signing_key: bytes) -> str:
        """计算数据块的签名
        
        Args:
            chunk_data: 数据块内容
            previous_signature: 前一个块的签名
            date: 请求时间戳
            signing_key: 签名密钥
            
        Returns:
            chunk的签名字符串
        """
        # 1. 构造字符串用于签名
        string_to_sign = (
            "AWS4-HMAC-SHA256-PAYLOAD\n"
            f"{date}\n"
            f"{date[:8]}/us-east-1/s3/aws4_request\n"
            f"{previous_signature}\n"
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855\n"  # 空字符串的hash
            f"{hashlib.sha256(chunk_data).hexdigest()}"
        )
        
        # 2. 计算签名
        signature = hmac.new(
            signing_key,
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

# 使用示例
async def main():
    client = S3Client(
        access_key="xxx",
        secret_key="xxx",
        endpoint_url="http://oss.i.xxx.com"
    )
    
    await client.download_file(
        bucket="xxx",
        key="xxx",
        output_path="./xxx"
    )

asyncio.run(main())

