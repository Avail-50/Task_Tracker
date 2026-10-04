import json
import os
import boto3
import uuid
from botocore.exceptions import ClientError

# import requests


def get_table():
    return boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def task_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    method = event.get("httpMethod")

    if method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
            title = body["title"].strip()
        except (KeyError, ValueError, AttributeError):
            return response(400, {"Error": "Body must be JSON with a 'title'"})

        if not title:
            return response(400, {"error": "'title' cannot be empty"})

        task = {
            "taskID": str(uuid.uuid4()),
            "title": title,
            "done": False,
        }
        get_table().put_item(Item=task)
        return response(201, task)

    if method == "GET":
        result = get_table().scan()
        return response(200, result["Items"])

    if method == "PATCH":
        task_id = (event.get("pathParameters") or {}).get("taskID")
        if not task_id:
            return response(400, {"Error": "Missing taskID in path"})

        try:
            body = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return response(400, {"error": "Body is not valid JSON"})

        done = body.get("done")
        if not isinstance(done, bool):
            return response(400, {"Error", "done must be true or false"})

        try:
            result = get_table().update_item(
                Key={"taskID": task_id},
                UpdateExpression="SET #d = :d",
                ConditionExpression="attribute_exists(taskID)",
                ExpressionAttributeNames={"#d": "done"},
                ExpressionAttributeValues={":d": done},
                ReturnValues="ALL_NEW",
            )
            return response(200, result['Attributes'])
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return response(404, {"error": "Task not found"})
            raise

    return response(405, {"Error": "Method not allowed"})
