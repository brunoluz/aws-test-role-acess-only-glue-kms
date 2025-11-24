locals {
  kms_alias = "alias/kms-glue-catalog"
}

resource "aws_kms_key" "kms_glue_catalog" {
  description             = "KMS key for encrypting Glue Data Catalog metadata"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowAccountAdmins"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_kms_alias" "kms_glue_catalog" {
  name          = local.kms_alias
  target_key_id = aws_kms_key.kms_glue_catalog.key_id
}

