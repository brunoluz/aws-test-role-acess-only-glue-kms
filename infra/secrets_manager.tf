resource "aws_secretsmanager_secret" "segredo_criptografado" {
  name        = "segredo_criptografado"
  description = "Segredo criptografado com kms_glue_catalog"

  kms_key_id = aws_kms_key.kms_glue_catalog.arn
}

resource "aws_secretsmanager_secret_version" "segredo_versao" {
  secret_id     = aws_secretsmanager_secret.segredo_criptografado.id
  secret_string = "segredo_sagrado"
}
