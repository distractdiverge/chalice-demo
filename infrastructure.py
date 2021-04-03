import boto3
from botocore.config import Config

state_table_name = "ppp-webbank-batch-state"


def get_dynamo_resource():
    return boto3.resource("dynamodb")


def get_dynamo_client():
    config = Config(region_name="us-west-2")
    return boto3.client("dynamodb", config=config)


def create_table(table_name):
    print(f"Creating DynamoDB: {table_name}")
    dynamodb = get_dynamo_resource()

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "webbank_identifier", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "webbank_identifier", "AttributeType": "S"}
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    print("Waiting for Table to be created")
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

    print(f"DONE\nNumber of entries: {table.item_count}")


def does_table_exist(table_name, dynamodb):
    table = None
    try:
        table = dynamodb.describe_table(TableName=table_name)
    except botocore.exceptions.ResourceNotFoundException as err:
        return false

    table_exists = table is not None
    is_table_active = table["Table"]["TableStatus"] == "ACTIVE"

    return table_exists and is_table_active


def create_ssm_param(name):
    client = boto3.client("ssm")
    # TODO: Create SSM Param


def create_ssm_params():
    create_ssm_param("/dm/prod/ppp/dropzone_user")
    create_ssm_param("/dm/prod/ppp/dropzone_password")


if __name__ == "__main__":
    print("#### Provisioning AWS Resources #####")

    dynamodb = get_dynamo_client()
    if does_table_exist(state_table_name, dynamodb):
        print("Table already exists")
    else:
        create_table(state_table_name, dynamodb)
        print("All resources have been created")

    print("DONE")
