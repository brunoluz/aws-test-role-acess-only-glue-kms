import boto3
import utils
import base64
from .utils import REGION


ROLE_NAME_ALL_KMS = "role-should-access-all-kms"

def test_assume_role_all_kms_and_get_glue_database():

    creds, _ = utils.assume_role(ROLE_NAME_ALL_KMS)

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

    creds, _ = utils.assume_role(ROLE_NAME_ALL_KMS)
    
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

    creds, _ = utils.assume_role(ROLE_NAME_ALL_KMS)
    
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

    creds, _ = utils.assume_role(ROLE_NAME_ALL_KMS)

    secrets = boto3.client(
        "secretsmanager",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )
    
    resp = secrets.get_secret_value(SecretId=secret_id)

    assert resp["SecretString"] == "segredo_sagrado"

def test_assume_role_all_kms_encrypt_decrypt_kms():

    creds, _ = utils.assume_role(ROLE_NAME_ALL_KMS)
    secret_text = "Texto super secreto"

    kms_client = boto3.client(
        "kms",
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=REGION,
    )

    encrypt_response = kms_client.encrypt(
        KeyId="alias/kms-glue-catalog",
        Plaintext=secret_text,
    )

    encrypted_text = base64.b64encode(encrypt_response["CiphertextBlob"]).decode("utf-8")

    decrypt_response = kms_client.decrypt(
        CiphertextBlob=base64.b64decode(encrypted_text.encode("utf-8"))
    )

    decrypted_text = decrypt_response["Plaintext"].decode("utf-8")

    assert decrypted_text == secret_text
