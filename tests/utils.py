import boto3

# Shared test configuration
REGION = "sa-east-1"
SESSION_NAME = "pytest-assume-role"

def assume_role(role_name: str):
    sts = boto3.client("sts", region_name=REGION)
    caller = sts.get_caller_identity()
    account = caller.get("Account")

    role_arn = f"arn:aws:iam::{account}:role/{role_name}"
    assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName=SESSION_NAME)
    creds = assumed.get("Credentials")

    return creds, account