import os
import boto3
import logging

aws_region = os.getenv("AWS_REGION")
table_name = os.getenv("TABLE_NAME")

# Logging configuration
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

ddb = boto3.resource("dynamodb", region_name=aws_region).Table(table_name)


def main(event, context):
    short_id = event.get("short_id")
    logging.info("long-url requested for short_id: %s", short_id)

    try:
        item = ddb.get_item(Key={"short_id": short_id})
        long_url = item.get("Item").get("long_url")
        logging.info("Successfully retreived long-url: %s requested for short_id: %s", long_url, short_id)
        # increase the hit number on the db entry of the url (for analytics)
        ddb.update_item(
            Key={"short_id": short_id},
            UpdateExpression="set hits = hits + :val",
            ExpressionAttributeValues={":val": 1},
        )

    except:
        logging.error("Can't find this short_id: %s, falling back to default", short_id)
        return {
            "statusCode": 301,
            "location": "https://zoph.io/",
        }

    return {"statusCode": 301, "location": long_url}
