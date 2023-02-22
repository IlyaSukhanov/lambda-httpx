import boto3
from httpx import BaseTransport, ByteStream, Request, Response
from lambda_invoke import LambdaSimpleProxy


class LambdaTransport(BaseTransport):
    def __init__(self, region=None):
        self.region = region
        self._lambda_client = None

    @property
    def lambda_client(self):
        if not self._lambda_client:
            self._lambda_client = boto3.client("lambda", region_name=self.region)
            print(boto3)
        return self._lambda_client

    def handle_request(self, request: Request):
        invoke = LambdaSimpleProxy(
            self.region,
            request.method,
            str(request.url),
            dict(request.headers),
            request.content,
        )
        lambda_response = invoke.send(self.lambda_client)
        response = Response(
            status_code=lambda_response.status_code,
            headers=lambda_response.headers,
            stream=ByteStream(lambda_response.body),
        )
        return response
