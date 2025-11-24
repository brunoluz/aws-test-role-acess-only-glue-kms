resource "aws_iam_role" "role_should_access_all_kms" {
  name = "role-should-access-all-kms"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/brunoluz"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "role_should_access_all_kms_policy" {
  name = "role-should-access-all-kms-policy"
  role = aws_iam_role.role_should_access_all_kms.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBasicLakeFormationAndGlue"
        Effect = "Allow"
        Action = [
          "lakeformation:*",
          "glue:*",
          "ram:*",
          "s3:*",
          "secretsmanager:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowKMSDecrypt"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          "ForAnyValue:StringEquals" = {
            "kms:ResourceAliases" = "${aws_kms_alias.kms_glue_catalog.name}"
          }
        }
      },
      {
        Sid    = "AllowKMSDecryptOnlyForGlueKmsAlias"
        Effect = "Deny"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
        Condition = {
          "ForAnyValue:StringNotEquals" = {
            "kms:ResourceAliases" = "${aws_kms_alias.kms_glue_catalog.name}"
          }
        }
      }
    ]
  })
}

