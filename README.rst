===============================
Lambda-httpx
===============================


.. image:: https://img.shields.io/pypi/v/lambda-httpx.svg
        :target: https://pypi.python.org/pypi/lambda-httpx


Lambda-httpx; use familiar async httpx library to access HTTP
enabled (simple proxy) AWS Lambda functions

Quick start
------------

Installation
````````````

.. code-block:: shell

    pip intall lambda-httpx

Usage Examples
``````````````

Lambda-httpx provides a transport which can be mounted with the httpx client.
This then relays over all requests with `http+lambda://` to AWS lambda whose name matches the hostname.


Using from existing event loop:

.. code-block:: python

    import httpx
    from lambda_httpx import AsyncLambdaTransport
    # ...
    async with AsyncLambdaTransport() as transport:
        mounts = {"http+lambda://": transport}
        async with httpx.AsyncClient(mounts=mounts) as client:
            response = await client.get("http+lambda://flaskexp-test/health")

Stand alone that calls endpoint 10 times asyncronously.

.. code-block:: python

    import asyncio
    import httpx
    from lambda_httpx import AsyncLambdaTransport

    async def main(count):
        async with AsyncLambdaTransport() as transport:
            mounts = {"http+lambda://": transport}
            async with httpx.AsyncClient(mounts=mounts) as client:
                coros = [client.get("http+lambda://flaskexp-test/health") for _ in range(count)]
                return await asyncio.gather(*coros)

    if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        responses = loop.run_until_complete(main(10))
        print(responses)
 
Lambda authorization is configured via `boto3`_, and can be set up using
`environment variables`_ or a `configuration file`_. Configuration file is
recommended. Example credential file ~/.aws/credentials:

.. code-block:: ini

    [default]
    aws_access_key_id =  XXXXXXXXXXXXXXXXXXXX
    aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

Similar to authorization, region can be configured either via the `environment
variable`_ `AWS_DEFAULT_REGION`, `configuration file`_. Region can also be set
on initialization of `AsyncLambdaTransport(region="us-west-2")`. Example configuration
file ~/.aws/config:

.. code-block:: ini

    [profile default]
    region = us-west-2

The lambdas must support `proxy integration`_, which is used commonly by frameworks
such as `Zappa`_, `Mangum`_.



.. _`boto3`: https://boto3.readthedocs.io/en/latest/
.. _`proxy integration`: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format
.. _`Zappa`: https://github.com/zappa/Zappa
.. _`Mangum`: https://mangum.io/
.. _`environment variables`: http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variables
.. _`configuration file`: http://boto3.readthedocs.io/en/latest/guide/configuration.html#shared-credentials-file
.. _`environment variable`: http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variable-configuration
.. _`configuration file option`: http://boto3.readthedocs.io/en/latest/guide/configuration.html#configuration-file

Why
---

In using REST microservice architecture it is important to be able to
conveniently make calls from one service to another. To use this pattern
in AWS serverless ecosphere along with Lambda one is practically forced
to stand up an API Gateway in front of the lambda. This has several distinct
disadvantages, all mostly along the lines of security.

* API Gateway publicly exposes endpoints
* API Gateway uses own authentication / authorization schema. While Lambda
  already supplies us with IAM.
* Extra dependencies in call chain. While availability is high, latency may
  still be of concern.

Over all, to reduce exposure of private sub-services, re-use IAM authentication
/ authorization and reduce latency.

How does its work
-----------------

Simple, we register a scheme name with httpx and use a lambda
specific `transport adapter`_ which translates a httpx request
to `lambda invoke`_ compatible with AWS API Gateway simple proxy format.

.. _`transport adapter`: https://www.python-httpx.org/advanced/#custom-transports
.. _`lambda invoke`: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html#Lambda.Client.invoke

See also
--------

* Lambda-requests_: Similar library that allows same functionality via python requests library.

.. _`Lambda-requests`: https://pypi.org/project/lambda-requests/
