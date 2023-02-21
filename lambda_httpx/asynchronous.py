import typing

import aioboto3
from httpx import AsyncBaseTransport, AsyncByteStream, Request, Response
from lambda_invoke import LambdaSimpleProxy


class ResponseStream(AsyncByteStream):
    def __init__(self, body: typing.List[bytes]) -> None:
        self._body = body

    async def __aiter__(self) -> typing.AsyncIterator[bytes]:
        yield self._body


class AsyncLambdaTransport(AsyncBaseTransport):
    def __init__(self, region=None):
        self.region = region
        self.lambda_client = None
        self.lambda_client_context = None

    async def __aenter__(self):
        self.boto_session = aioboto3.Session()
        self.lambda_client = self.boto_session.client("lambda", region_name=self.region)
        self.lambda_client_context = await self.lambda_client.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        return await self.lambda_client.__aexit__(*args, **kwargs)

    async def handle_async_request(self, request: Request):
        invoke = LambdaSimpleProxy(
            self.region,
            request.method,
            str(request.url),
            dict(request.headers),
            request.content,
        )
        lambda_response = await invoke.async_send(self.lambda_client_context)

        response = Response(
            status_code=lambda_response.status_code,
            headers=lambda_response.headers,
            stream=ResponseStream(lambda_response.body),
        )
        return response
