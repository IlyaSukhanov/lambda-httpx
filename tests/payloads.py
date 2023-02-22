import asyncio


def reply():
    return b'{"body": "ewogICJzdGF0dXMiOiAiVVAiCn0K", "isBase64Encoded": "true", "statusCode": 200, "headers": {"Content-Type": "application/json", "X-Request-ID": "", "Content-Length": "21"}}'  # noqa: E501


async def delayed_reply():
    await asyncio.sleep(0.1)
    return reply()
