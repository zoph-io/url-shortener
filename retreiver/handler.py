import os
import boto3

aws_region = os.getenv("AWS_REGION")
table_name = os.getenv("TABLE_NAME")

ddb = boto3.resource("dynamodb", region_name=aws_region).Table(table_name)


def main(event, context):
    short_id = event.get("short_id")

    try:
        item = ddb.get_item(Key={"short_id": short_id})
        long_url = item.get("Item").get("long_url")
        # increase the hit number on the db entry of the url (analytics?)
        ddb.update_item(
            Key={"short_id": short_id},
            UpdateExpression="set hits = hits + :val",
            ExpressionAttributeValues={":val": 1},
        )

    except:
        return {
            "statusCode": 301,
            "location": "https://zoph.io/",
        }

    return {"statusCode": 301, "location": long_url}
