import boto3
import utils
from .utils import REGION
import pytest

ROLE_NAME = "role-should-access-all-kms"

def test_assume_role_all_kms_and_get_glue_database():

    creds, _ = utils.assume_role(ROLE_NAME)

    glue = boto3.client(
		"glue",
		aws_access_key_id=creds["AccessKeyId"],
		aws_secret_access_key=creds["SecretAccessKey"],
		aws_session_token=creds["SessionToken"],
		region_name=REGION,
	)

    resp = glue.get_database(Name="glue_encrypted_database")

    assert resp["Database"].get("Name") == "glue_encrypted_database"


def test_assume_role_all_kms_and_get_glue_table():

    creds, _ = utils.assume_role(ROLE_NAME)
    
    glue = boto3.client(
		"glue",
		aws_access_key_id=creds["AccessKeyId"],
		aws_secret_access_key=creds["SecretAccessKey"],
		aws_session_token=creds["SessionToken"],
		region_name=REGION,
	)

    resp = glue.get_table(
        DatabaseName="glue_encrypted_database",
        Name="glue_encrypted_table"
	)

    assert resp["Table"].get("Name") == "glue_encrypted_table"


def test_assume_role_all_kms_and_s3_object_kms_denied():

    creds, _ = utils.assume_role(ROLE_NAME)
    
    bucket = "brunoluz-teste-kms"
    key = "arquivo.txt"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )
    
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    body = s3_object["Body"].read()
    text = body.decode("utf-8").strip()

    assert text == "brunoluz"


def test_assume_role_all_kms_and_get_secret_manager_value():

    secret_id = "segredo_criptografado"
    expected_value = "segredo_sagrado"

    creds, _ = utils.assume_role(ROLE_NAME)

    secrets = boto3.client(
        "secretsmanager",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )
    
    resp = secrets.get_secret_value(SecretId=secret_id)

    assert resp["SecretString"] == "segredo_sagrado"
