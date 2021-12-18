import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import httpx
from with_time.timer import PrintingTimer

from lambda_httpx import AsyncLambdaTransport


class PatcherBase:
    def add_patcher(self, target, new=DEFAULT, new_callable=None):
        target_patch = patch(target, new, new_callable)
        self.addCleanup(target_patch.stop)
        return target_patch.start()


async def delayed_reply():
    await asyncio.sleep(0.1)
    return b'{"body": "ewogICJzdGF0dXMiOiAiVVAiCn0K", "isBase64Encoded": "true", "statusCode": 200, "headers": {"Content-Type": "application/json", "X-Request-ID": "", "Content-Length": "21"}}'  # noqa: E501


async def call_many(count):
    async with AsyncLambdaTransport() as transport:
        async with httpx.AsyncClient(transport=transport) as client:
            coros = [
                client.get("http+lambda://flaskexp-test/health") for _ in range(count)
            ]
            await asyncio.gather(*coros)


class TestSimpleProxyAsync(PatcherBase, IsolatedAsyncioTestCase):
    def setUp(self):

        mock_session = MagicMock()
        mock_invoke_result = MagicMock()
        mock_invoke_result().__getitem__().read = delayed_reply
        mock_client_context = MagicMock()
        mock_client_context.invoke = AsyncMock(side_effect=mock_invoke_result)

        mock_session().Session().client().__aenter__ = AsyncMock(
            return_value=mock_client_context
        )

        self.aiboto3 = self.add_patcher(
            "lambda_httpx.lambda_httpx.aioboto3", mock_session()
        )

    async def test_200_ok(self):
        async with AsyncLambdaTransport() as transport:
            async with httpx.AsyncClient(transport=transport) as client:
                response = await client.get("http+lambda://flaskexp-test/health")

                assert response.status_code == 200
                assert response.json() == {"status": "UP"}
                assert response.headers["Content-Type"] == "application/json"

    def test_async(self):
        # Ensure 10 calls are not more than 2x slower than one call
        times = 10
        with PrintingTimer() as timer:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(call_many(1))
        one_call_time = timer.elapsed_time

        with PrintingTimer() as timer:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(call_many(times))
        many_call_time = timer.elapsed_time

        assert one_call_time < 0.15
        assert one_call_time > 0.05
        assert many_call_time < one_call_time * 2
