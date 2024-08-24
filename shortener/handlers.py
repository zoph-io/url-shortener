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
import math

# Logging configuration
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Set variables
domain = os.getenv("DOMAIN")
sub_domain = os.getenv("SUB_DOMAIN")
aws_region = os.getenv("AWS_REGION")
fallback_url = os.getenv("FALLBACK_URL")
table_name = os.getenv("TABLE_NAME")
min_char = int(os.getenv("MIN_CHAR"))
max_char = int(os.getenv("MAX_CHAR"))
string_format = ascii_letters + digits

# CORS configuration
website_url = "https://short." + domain
api_endpoint = "https://" + sub_domain + "." + domain
allowed_origins = [api_endpoint, website_url]

ddb = boto3.resource("dynamodb", region_name=aws_region).Table(table_name)

def cors_setup(event):
    if "origin" in event["headers"]:
        logging.info("Origin header detected: %s", event["headers"]["origin"])
        origin = event["headers"]["origin"]
        if origin in allowed_origins:
            logging.info("Origin %s is allowed", origin)
        else:
            origin = "https://www.accessdenied.com/" # =)
    else:
        origin = "https://www.accessdenied.com/" # =)
    
    return origin

def generate_timestamp():
    response = strftime("%Y-%m-%dT%H:%M:%S")
    return response


def expiry_date(days=7):
    if days is None or days == 0: # Nothing sent
        days = 7
    if days < 0: # Negative value => almost infinite value (ie 100 years)
        days = 36500
        # Note: EPOCH may have an overflow issue for date after Tuesday, January 19, 2038
        #       https://www.epoch101.com/The-2038-Problem
    ttl = days * 3600 * 24
    response = int(time()) + int(ttl)
    return response


def check_id(short_id):
    response = ddb.get_item(Key={"short_id": short_id})
    if "Item" in response:
        print("short_id already exists in Table, generating a new one")
        return False
    else:
        print("newly generate_id is not used, going forward:", short_id)
        return True

def generate_id( human_readble = False ):

    vowels = ['a', 'e', 'i', 'o', 'u', 'y']
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'v', 'w', 'x',  'z']
    syllabs = math.ceil(randint(min_char, max_char) / 2)
    
    
    unique = False
    while not unique:
        if not human_readble:
            short_id = "".join(
                choice(string_format) for x in range(randint(min_char, max_char))
            )
        else:
            short_id = "".join(
                (choice(consonants)+choice(vowels)) for x in range(syllabs)      
            )
        unique = check_id(short_id)

    return short_id    


def main(event, context):
    logging.info("===> Event: %s", event)
    if "short_id" in event:
        answer = retreiver(event, context)

        return answer
    else:
        if "/create" in event["path"] and event["httpMethod"] == "POST":
            answer = create(event, context)
        else:
            cors = cors_setup(event)
            answer = {
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": cors,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps({"Error": "Access Denied"}),
            }

    return answer


def create(event, context):
    analytics = {}

    # Handle empty long_url
    if not json.loads(event.get("body")).get("long_url"):
        cors = cors_setup(event)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": cors,
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": json.dumps({"message": "Empty url field"}),
        }
    else:
        # Handle wrong url
        if validators.url(json.loads(event.get("body")).get("long_url")):
            long_url = json.loads(event.get("body")).get("long_url")
        else:
            cors = cors_setup(event)
            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": cors,
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": json.dumps({"message": "Malformed URL"}),
            }

    if not json.loads(event.get("body")).get("human_readable"):
        short_id = generate_id(False)
    else:
        short_id = generate_id(True)
    short_url = "https://" + sub_domain + "." + domain + "/" + short_id



    # Try to read the ttl_in_days value
    try:
        ttl = json.loads(event.get("body")).get("ttl_in_days")
    except:
        ttl = 0

    timestamp = generate_timestamp()
    ttl_value = expiry_date(ttl)

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
        cors = cors_setup(event)
        answer = {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": cors,
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

        if "Item" in item:
            long_url = item.get("Item").get("long_url")
        else:
            return {
                "statusCode": 301,
                "location": fallback_url,
            }
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
