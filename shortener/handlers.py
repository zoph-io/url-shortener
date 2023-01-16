import os
import json
from botocore.exceptions import ClientError
import boto3
from string import ascii_letters, digits
from random import choice, randint
from time import strftime, time
from urllib import parse
import logging
import validators

# Logging configuration
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

domain = os.getenv("DOMAIN")
sub_domain = os.getenv("SUB_DOMAIN")
aws_region = os.getenv("AWS_REGION")
fallback_url = os.getenv("FALLBACK_URL")
table_name = os.getenv("TABLE_NAME")
min_char = int(os.getenv("MIN_CHAR"))
max_char = int(os.getenv("MAX_CHAR"))
string_format = ascii_letters + digits

ddb = boto3.resource("dynamodb", region_name=aws_region).Table(table_name)


def generate_timestamp():
    response = strftime("%Y-%m-%dT%H:%M:%S")
    return response


def expiry_date():
    response = int(time()) + int(604800)
    return response


def check_id(short_id):
    if "Item" in ddb.get_item(Key={"short_id": short_id}):
        response = generate_id()
    else:
        return short_id


def generate_id():
    short_id = "".join(
        choice(string_format) for x in range(randint(min_char, max_char))
    )
    response = check_id(short_id)

    return response


def main(event, context):
    logging.info("===> Event: %s", event)
    if "short_id" in event:
        answer = retreiver(event, context)

        return answer
    else:
        if "/create" in event["path"] and event["httpMethod"] == "POST":
            answer = create(event, context)

        return answer


def create(event, context):
    analytics = {}
    short_id = generate_id()
    short_url = "https://" + sub_domain + "." + domain + "/" + short_id

    # Handle empty long_url
    if not json.loads(event.get("body")).get("long_url"):
        answer = {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"message": "Empty url field"}),
        }
    else:
        # Handle wrong url
        if validators.url(json.loads(event.get("body")).get("long_url")):
            long_url = json.loads(event.get("body")).get("long_url")
        else:
            answer = {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps({"message": "Malformed URL"}),
            }

    timestamp = generate_timestamp()
    ttl_value = expiry_date()

    analytics["user_agent"] = event.get("headers").get("User-Agent")
    analytics["source_ip"] = event.get("headers").get("X-Forwarded-For")
    analytics["xray_trace_id"] = event.get("headers").get("X-Amzn-Trace-Id")
    logging.info("Generating analytics: %s", analytics)

    if len(parse.urlsplit(long_url).query) > 0:
        url_params = dict(parse.parse_qsl(parse.urlsplit(long_url).query))
        for k in url_params:
            analytics[k] = url_params[k]
    else:
        logging.info("No parameter detected in this url: %s", long_url)

    try:
        response = ddb.put_item(
            Item={
                "short_id": short_id,
                "created_at": timestamp,
                "ttl": int(ttl_value),
                "short_url": short_url,
                "long_url": long_url,
                "analytics": analytics,
                "hits": int(0),
            }
        )

        body = {
            "short_id": short_id,
            "created_at": timestamp,
            "ttl": int(ttl_value),
            "short_url": short_url,
            "long_url": long_url,
        }

        answer = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps(body),
        }
    except ClientError as e:
        logging.error("Error while writing new short_url to table: %s", e)

    return answer


def retreiver(event, context):
    short_id = event.get("short_id")
    logging.info("long-url requested for short_id: %s", short_id)

    try:
        item = ddb.get_item(Key={"short_id": short_id})
        long_url = item.get("Item").get("long_url")
        logging.info(
            "Successfully retreived long-url: %s requested for short_id: %s",
            long_url,
            short_id,
        )
        # Stats: increase the hit number on the db entry of the url (for analytics)
        try:
            ddb.update_item(
                Key={"short_id": short_id},
                UpdateExpression="set hits = hits + :val",
                ExpressionAttributeValues={":val": 1},
            )
        except ClientError as error:
            logging.error(
                "Failed to increase the stats for: %s with: %s", short_id, error
            )
    except ClientError as err:
        long_url = fallback_url
        logging.error(
            "Can't find this short_id: %s, falling back to default: %s", short_id, err
        )

    answer = {
        "statusCode": 301,
        "location": long_url,
    }

    return answer
