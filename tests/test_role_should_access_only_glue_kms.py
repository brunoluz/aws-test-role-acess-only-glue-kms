import boto3
import botocore.exceptions
import pytest
import re
import utils
from .utils import REGION

ROLE_NAME = "role-should-access-only-glue-kms"

def test_assume_role_only_glue_and_get_glue_database():

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


def test_assume_role_only_glue_and_get_glue_table():

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


def test_assume_role_only_glue_and_s3_object_kms_denied():

    creds, account = utils.assume_role(ROLE_NAME)
    
    bucket = "brunoluz-teste-kms"
    key = "arquivo.txt"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )

    try:
        s3.get_object(Bucket=bucket, Key=key)
        pytest.fail("Abertura do objeto S3 teve sucesso inesperado; esperava falha por KMS.")

    except botocore.exceptions.ClientError as exc:
        err = exc.response.get("Error")
        err_code = err.get("Code")
        err_message = err.get("Message")

        # Substitui qualquer UUID que apareça no ARN da chave KMS antes de verificar a mensagem.
        uuid_regex = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
        redacted_message = uuid_regex.sub("<UUID>", err_message)

        expected_redacted = (
            f"User: arn:aws:sts::{account}:assumed-role/role-should-access-only-glue-kms/pytest-assume-role "
            f"is not authorized to perform: kms:Decrypt on resource: arn:aws:kms:{REGION}:{account}:key/<UUID> "
            f"with an explicit deny in an identity-based policy"
        )

        assert err_code == "AccessDenied"
        assert redacted_message == expected_redacted


def test_assume_role_only_glue_and_get_secret_manager_value():

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
    
    try:
        secrets.get_secret_value(SecretId=secret_id)
        pytest.fail("Abertura do secrets manager teve sucesso inesperado; esperava falha por KMS.")
    except botocore.exceptions.ClientError as exc:
        err = exc.response.get("Error")
        err_code = err.get("Code")
        err_message = err.get("Message")

    assert err_code == "AccessDeniedException"
    assert err_message == "Access to KMS is not allowed"