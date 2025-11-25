import boto3
import re

# Shared test configuration
REGION = "sa-east-1"
SESSION_NAME = "pytest-assume-role"
ROLE_NAME_ONLY_GLUE = "role-should-access-only-glue-kms"
ROLE_NAME_ALL_KMS = "role-should-access-all-kms"

def assume_role(role_name: str):
    sts = boto3.client("sts", region_name=REGION)
    caller = sts.get_caller_identity()
    account = caller.get("Account")

    role_arn = f"arn:aws:iam::{account}:role/{role_name}"
    assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName=SESSION_NAME)
    creds = assumed.get("Credentials")

    return creds, account

def substitute_uuid_in_string(s: str, uuid_replacement: str) -> str:
    uuid_regex = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    return re.sub(uuid_regex, uuid_replacement, s)