import os
import boto3
import botocore.exceptions
import pytest


def test_assume_role_and_get_glue_database():

    """Testa assume-role para `role-should-access-only-glue-kms` e chama Glue.get_database.

	Passos:
	1) Usa STS para descobrir a conta e montar o ARN da role `role-should-access-only-glue-kms`.
	2) Assume a role e obtém credenciais temporárias.
	3) Usa as credenciais temporárias para criar um cliente Glue e chama `get_database(Name='glue_encrypted_database')`.

	Observações:
	- Este teste executa chamadas reais à AWS. É necessário ter credenciais configuradas
	  (env vars, profile, ou IAM role no ambiente de execução) e permissões para
	  realizar `sts:AssumeRole` e `glue:GetDatabase` com a role alvo.
	"""

	# 1) Obter account id via STS (usa credenciais padrão da máquina/ambiente)
    sts = boto3.client("sts")
    caller = sts.get_caller_identity()
    region = "sa-east-1"

	# 2) Assume a role e obtém credenciais temporárias.
    account = caller.get("Account")
    role_arn = f"arn:aws:iam::{account}:role/role-should-access-only-glue-kms"
    assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName="pytest-assume-role")
    creds = assumed.get("Credentials")
    
	# 3) Usa as credenciais temporárias para criar um cliente Glue e chama `get_database(Name='glue_encrypted_database')`.
    glue = boto3.client(
		"glue",
		aws_access_key_id=creds["AccessKeyId"],
		aws_secret_access_key=creds["SecretAccessKey"],
		aws_session_token=creds["SessionToken"],
		region_name=os.getenv("AWS_REGION", region),
	)

    resp = glue.get_database(Name="glue_encrypted_database")

    assert resp["Database"].get("Name") == "glue_encrypted_database"


def test_assume_role_and_get_glue_table():

    """Testa assume-role para `role-should-access-only-glue-kms` e chama Glue.get_table.

	Passos:
	1) Usa STS para descobrir a conta e montar o ARN da role `role-should-access-only-glue-kms`.
	2) Assume a role e obtém credenciais temporárias.
	3) Usa as credenciais temporárias para criar um cliente Glue e chama `get_table(DatabaseName="glue_encrypted_database", Name="glue_encrypted_table")`.

	Observações:
	- Este teste executa chamadas reais à AWS. É necessário ter credenciais configuradas
	  (env vars, profile, ou IAM role no ambiente de execução) e permissões para
	  realizar `sts:AssumeRole` e `glue:GetTable` com a role alvo.
	"""

	# 1) Obter account id via STS (usa credenciais padrão da máquina/ambiente)
    sts = boto3.client("sts")
    caller = sts.get_caller_identity()
    region = "sa-east-1"

	# 2) Assume a role e obtém credenciais temporárias.
    account = caller.get("Account")
    role_arn = f"arn:aws:iam::{account}:role/role-should-access-only-glue-kms"
    assumed = sts.assume_role(RoleArn=role_arn, RoleSessionName="pytest-assume-role")
    creds = assumed.get("Credentials")
    
	# 3) Usa as credenciais temporárias para criar um cliente Glue e chama `get_database(Name='glue_encrypted_database')`.
    glue = boto3.client(
		"glue",
		aws_access_key_id=creds["AccessKeyId"],
		aws_secret_access_key=creds["SecretAccessKey"],
		aws_session_token=creds["SessionToken"],
		region_name=os.getenv("AWS_REGION", region),
	)

    resp = glue.get_table(
        DatabaseName="glue_encrypted_database",
        Name="glue_encrypted_table"
	)

    assert resp["Table"].get("Name") == "glue_encrypted_table"

