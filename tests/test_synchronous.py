from unittest import TestCase

import httpx
from patcher import PatcherBase
from payloads import reply

from lambda_httpx import LambdaTransport


class TestLambdaTransport(PatcherBase, TestCase):
    def setUp(self):
        self.boto3 = self.add_patcher("lambda_httpx.synchronous.boto3")
        self.boto3.client().invoke().__getitem__().read = reply

    def test_bare(self):
        mounts = {"http+lambda://": LambdaTransport()}
        client = httpx.Client(mounts=mounts)
        response = client.get("http+lambda://flaskexp-test/health")
        assert response.status_code == 200
        assert response.json() == {"status": "UP"}
        assert response.headers["Content-Type"] == "application/json"

    def test_context_managed(self):
        with LambdaTransport() as transport:
            mounts = {"http+lambda://": transport}
            with httpx.Client(mounts=mounts) as client:
                response = client.get("http+lambda://flaskexp-test/health")

                assert response.status_code == 200
                assert response.json() == {"status": "UP"}
                assert response.headers["Content-Type"] == "application/json"
