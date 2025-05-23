import aiohttp
from curl_cffi import requests
from curl_cffi.requests.exceptions import HTTPError


async def aiohttp_raise_for_status_with_text(response: aiohttp.ClientResponse):
    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as e:
        try:
            response_text = await response.text()
        except Exception:
            response_text = None
        raise aiohttp.ClientResponseError(
            request_info=e.request_info,
            history=e.history,
            status=e.status,
            message=f"{e.message} - {response_text=}",
            headers=e.headers,
        ) from e


def curl_cffi_raise_for_status_with_text(response: requests.Response):
    try:
        response.raise_for_status()
    except HTTPError as e:
        try:
            response_text = response.text
        except Exception:
            response_text = None
        raise HTTPError(
            msg=f"{e} - {response_text=}",
            code=e.code,
            response=response,
        ) from e
