resource "aws_iam_role" "role_should_access_only_glue_kms" {
  name = "role-should-access-only-glue-kms"

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

resource "aws_iam_role_policy" "role_should_access_only_glue_kms_policy" {
  name = "role-should-access-only-glue-kms-policy"
  role = aws_iam_role.role_should_access_only_glue_kms.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBasicLakeFormationAndGlue"
        Effect = "Allow"
        Action = [
          "lakeformation:*",
          "glue:*",
          "ram:*"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowKMSDecrypt"
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "glue.${var.aws_region}.amazonaws.com"
          }
          "ForAnyValue:StringEquals" = {
            "kms:ResourceAliases" = "${aws_kms_alias.kms_glue_catalog.name}"
          }
        }
      },
      {
        Sid    = "AllowKMSDecryptOnlyForGlueService"
        Effect = "Deny"
        Action = [
          "kms:Decrypt"
        ]
        Resource = "*"
        Condition = {
          StringNotEquals = {
            "kms:ViaService" = "glue.${var.aws_region}.amazonaws.com"
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

