terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "sa-east-1"
}


data "aws_caller_identity" "current" {}

// KMS key for Glue Data Catalog metadata
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

// Alias for the KMS key
resource "aws_kms_alias" "kms_glue_catalog" {
  name          = "alias/kms-glue-catalog"
  target_key_id = aws_kms_key.kms_glue_catalog.key_id
}

// Configure Glue Data Catalog to use the KMS key for metadata encryption
resource "aws_glue_data_catalog_encryption_settings" "catalog_encryption" {
  data_catalog_encryption_settings {
    encryption_at_rest {
      catalog_encryption_mode = "SSE-KMS"
      sse_aws_kms_key_id      = aws_kms_key.kms_glue_catalog.arn
    }

    connection_password_encryption {
      return_connection_password_encrypted = false
    }
  }
}

resource "aws_iam_role" "brunoluz_test_kms_role" {
  name = "brunoluz-test-kms-role"

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

// Política inline que nega explicitamente todas ações KMS para a role
resource "aws_iam_role_policy" "brunoluz_test_kms_allow_basic" {
  name = "brunoluz-test-kms-allow-basic"
  role = aws_iam_role.brunoluz_test_kms_role.name

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
          "servicecatalog:*"
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
            "kms:ViaService" = "glue.${var.aws_region}.amazonaws.com" # "kms:ViaService" = "s3.${var.aws_region}.amazonaws.com"
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

// Bucket S3 para uso pelo Glue
resource "aws_s3_bucket" "brunoluz_teste_kms" {
  bucket        = "brunoluz-teste-kms"
  force_destroy = true

  tags = {
    Name = "brunoluz-teste-kms"
    Env  = "dev"
  }
}

// Glue Catalog Database usando a location do bucket S3
resource "aws_glue_catalog_database" "brunoluz_test_db" {
  name         = "brunoluz_test_db"
  description  = "Glue catalog database for brunoluz tests"
  location_uri = "s3://${aws_s3_bucket.brunoluz_teste_kms.bucket}/"

  depends_on = [aws_glue_data_catalog_encryption_settings.catalog_encryption]
}

// Glue Catalog Table (Avro)
resource "aws_glue_catalog_table" "brunoluz_test_kms_table" {
  name          = "brunoluz_test_kms_table"
  database_name = aws_glue_catalog_database.brunoluz_test_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "avro"
  }

  storage_descriptor {

    columns {
      name    = "id"
      type    = "string"
      comment = "identifier"
    }

    location = "s3://${aws_s3_bucket.brunoluz_teste_kms.bucket}/brunoluz_test_kms_table/"

    input_format  = "org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat"

    ser_de_info {
      name                  = "avro_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.avro.AvroSerDe"
      parameters            = {}
    }
  }
}

