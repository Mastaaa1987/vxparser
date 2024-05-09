import httpx
from starlette import status as starlette_status
from starlette.datastructures import Headers as StarletteHeaders
from starlette.datastructures import MutableHeaders as StarletteMutableHeaders
from starlette.background import BackgroundTasks
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
from starlette.responses import StreamingResponse

from utils.common import Logger as Logger

# courtesy of fastapi-proxy-lib:
# https://github.com/WSH032/fastapi-proxy-lib/blob/main/src/fastapi_proxy_lib/core/http.py#L445
# for proxying through https see:
# https://github.com/encode/httpx/blob/e34df7a7a19b5ebdbad59a0b7e1a54b4f011811b/httpx/dispatch/proxy_http.py

_400_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY = (
    httpx.InvalidURL,
    httpx.UnsupportedProtocol,
    httpx.ProtocolError,
)
"""These errors need to be caught.
When:
- client.build_request
- client.send
"""

_500_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY = (
    httpx.ConnectError,
)
"""These errors need to be caught and return 5xx status_code.
When:
- client.build_request
- client.send
"""


def _change_client_header(
    headers: StarletteHeaders, target_url: httpx.URL,
) -> StarletteMutableHeaders:
    """Change client request headers for sending to proxy server.

    - Change "host" header to `target_url.netloc.decode("ascii")`.
    - If "Cookie" header is not in headers,
        will forcibly add a empty "Cookie" header
        to avoid httpx.AsyncClient automatically add another user cookiejar.
    - Will remove "close" value in "connection" header, and add "keep-alive" value to it.
    - And remove "keep-alive" header.

    Args:
        headers: original client request headers.
        target_url: httpx.URL of target server url.

    Returns:
        New requests headers, the **copy** of original input headers.
    """
    new_headers = headers.mutablecopy()
    new_headers["host"] = target_url.netloc.decode("ascii")
    new_headers["connection"] = "keep-alive"
    if "Cookie" not in new_headers:  # case-insensitive
        new_headers["Cookie"] = ""
    if "keep-alive" in new_headers:
        del new_headers["keep-alive"]
    if "origin" in new_headers:
        del new_headers["origin"] # skip CORS
    if "upgrade-insecure-requests" in new_headers:
        del new_headers["upgrade-insecure-requests"] # skip HTTPS
    # remove traces
    if "referer" in new_headers:
        del new_headers["referer"]
    if "accept-language" in new_headers:
        new_headers["accept-language"] = "en"

    return new_headers

def _change_server_header(
    headers: httpx.Headers,
) -> httpx.Headers:
    """Change server response headers for sending to client.

    - Removes "connection and" "keep-alive" header.

    Args:
        headers: server response headers

    Returns:
        The **original headers**, but **adapted**.
    """
    if "connection" in headers:
        del headers["connection"]
    if "keep-alive" in headers:
        del headers["keep-alive"]
     # re-added by Uvicorn
    if "server" in headers:
        del headers["server"]
    if "date" in headers:
        del headers["date"]

    return headers


class ForwardHttpProxy():
    """ForwardHttpProxy class.

    Attributes:
        client: The httpx.AsyncClient to send http requests.
        follow_redirects: Whether follow redirects of proxy server.
    """

    client: httpx.AsyncClient
    follow_redirects: bool

    def __init__(
        self, client: httpx.AsyncClient = None, follow_redirects: bool = True,
    ) -> None:
        """Forward http proxy.

        Args:
            client: The httpx.AsyncClient to send http requests. Defaults to None.
                if None, will create a new httpx.AsyncClient configured for streaming,
                else will use the given httpx.AsyncClient.
            follow_redirects: Whether follow redirects of proxy server. Defaults to True.
        """

        self.client = client if client is not None else httpx.AsyncClient(verify=False, timeout=None, trust_env=False)
        self.follow_redirects = follow_redirects

    async def stream(
        self,
        request: StarletteRequest,
        stream_url: str,
    ) -> StarletteResponse:
        """Send request to target server.

        Args:
            request: origin `starlette.requests.Request` from IPTV-Client
            stream_url: The resolved url of remote streaming server.

        Returns:
            The response from target server.
        """

        try:
            target_url = httpx.URL(stream_url)
        except httpx.InvalidURL as e:
            return JSONResponse(
                content={detail: {err_type: type(e).__name__, msg: str(e)}},
                status_code=starlette_status.HTTP_400_BAD_REQUEST,
            )

        try:
            return await self.send_request_to_target(
                request=request, target_url=target_url,
            )
        except _400_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY as e:
            return JSONResponse(
                content={detail: {err_type: type(e).__name__, msg: str(e)}},
                status_code=starlette_status.HTTP_400_BAD_REQUEST,
            )
        except _500_ERROR_NEED_TO_BE_CATCHED_IN_FORWARD_PROXY as e:
            return JSONResponse(
                content={detail: {err_type: type(e).__name__, msg: str(e)}},
                status_code=starlette_status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def send_request_to_target(
        self,
        request: StarletteRequest,
        target_url: httpx.URL,
    ) -> StarletteResponse:
        """Change request headers and send request to target url.

        Args:
            request: the original client request.
            target_url: target url that request will be sent to.

        Returns:
            The response from target url.
        """

        proxy_header = _change_client_header(
            headers=request.headers, target_url=target_url,
        )

        if b"vavoo_auth" in target_url.query:
            proxy_header["user-agent"] = "VAVOO/2.6"

        self.client.cookies.clear()

        # https://www.python-httpx.org/compatibility/
        proxy_request = self.client.build_request(
            method=request.method,
            url=target_url,
            params=request.query_params,
            headers=proxy_header,
            content=None,
        )

        Logger(9, "proxying: clienttimeout:%s ; clienthead:%s, url:%s ; head:%s" %(
            self.client.timeout,
            request.headers,
            str(proxy_request.url),
            proxy_request.headers,
            )
        )

        proxy_response = await self.client.send(
            proxy_request,
            stream=True,
            follow_redirects=self.follow_redirects,
        )

        tasks = BackgroundTasks()
        tasks.add_task(proxy_response.aclose)

        if proxy_response.status_code == 302:
            Logger(3, "Warn - follow_redirects=False reveals your privacy!", "proxy")
            if "cloudflare" in proxy_response.headers["server"]:
                Logger(9, "CLOUDFARE_PROTECTED_RESOURCE: %s" %(proxy_response.headers["location"]))
            # manually handle (maybe repeatedly until .next_request is None)
            proxy_response2 = await self.client.send(proxy_response.next_request, stream=True, follow_redirects=self.follow_redirects)
            tasks.add_task(proxy_response2.aclose)
            proxy_response = proxy_response2

        if "cloudflare" in proxy_response.headers["server"]:
            Logger(9, "CLOUDFARE_PROTECTED_RESOURCE: status:%s ; head:%s" %(proxy_response.status_code, proxy_response.headers))

        proxy_response_headers = _change_server_header(headers=proxy_response.headers)
        client_origin = "*"
        if "origin" in request.headers:
            client_origin = request.headers["origin"]
        proxy_response_headers.update({"Access-Control-Allow-Origin": client_origin})
        proxy_response_headers.update({"Access-Control-Allow-Methods": request.method})
        proxy_response_headers.update({"Access-Control-Allow-Headers": "*"})
        proxy_response_headers.update({"Access-Control-Max-Age": "86400"})

        Logger(9, "proxied: status:%s ; url:%s ; head:%s" %(
            str(proxy_response.status_code),
            str(proxy_response.url),
            proxy_response_headers,
            )
        )

        return StreamingResponse(
            content=proxy_response.aiter_raw(),
            status_code=proxy_response.status_code,
            headers=proxy_response_headers,
            background=tasks,
        )

    async def aclose(self) -> None:
        """Close AsyncClient.

        Equal to:
            await self.client.aclose()
        """
        await self.client.aclose()
