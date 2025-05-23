import pytest
from unittest.mock import MagicMock
import aiohttp
from curl_cffi import requests
from curl_cffi.requests.exceptions import HTTPError
from omni_pathlib.utils.raise_for_status_with_text import (
    aiohttp_raise_for_status_with_text,
    curl_cffi_raise_for_status_with_text,
)


def test_curl_cffi_raise_for_status_with_text():
    """测试 curl_cffi_raise_for_status_with_text 函数处理 HTTP 错误"""
    # 创建模拟的 Response 对象
    mock_response = MagicMock(spec=requests.Response)
    mock_response.text = "测试错误响应"

    # 模拟 response.raise_for_status() 抛出 HTTPError
    original_error = HTTPError("HTTP 错误", code=0, response=mock_response)

    # 设置 raise_for_status 抛出错误
    mock_response.raise_for_status.side_effect = original_error

    # 验证函数引发带有正确代码和响应的 HTTPError
    with pytest.raises(HTTPError) as excinfo:
        curl_cffi_raise_for_status_with_text(mock_response)

    # 验证异常包含原始错误代码和正确的响应对象
    assert excinfo.value.code == original_error.code
    assert excinfo.value.response == mock_response
    # 验证错误消息包含响应文本
    assert "测试错误响应" in str(excinfo.value)


@pytest.mark.asyncio
async def test_aiohttp_raise_for_status_with_text():
    """测试 aiohttp_raise_for_status_with_text 函数处理 HTTP 错误"""
    # 创建模拟的 ClientResponse 对象
    mock_response = MagicMock(spec=aiohttp.ClientResponse)

    # 模拟异步 text() 方法
    async def mock_text():
        return "测试错误响应"

    mock_response.text = mock_text

    # 模拟 response.raise_for_status() 抛出 ClientResponseError
    original_error = aiohttp.ClientResponseError(
        request_info=MagicMock(),
        history=(),
        status=500,
        message="服务器错误",
        headers=MagicMock(),
    )

    # 设置 raise_for_status 抛出错误
    mock_response.raise_for_status.side_effect = original_error

    # 验证函数引发带有正确状态和消息的 ClientResponseError
    with pytest.raises(aiohttp.ClientResponseError) as excinfo:
        await aiohttp_raise_for_status_with_text(mock_response)

    # 验证异常包含原始错误状态和消息包含响应文本
    assert excinfo.value.status == original_error.status
    assert "测试错误响应" in excinfo.value.message
