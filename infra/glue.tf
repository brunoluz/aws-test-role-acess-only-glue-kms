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

resource "aws_glue_catalog_database" "glue_encrypted_database" {
  name         = "glue_encrypted_database"
  location_uri = "s3://${aws_s3_bucket.brunoluz_teste_kms.bucket}/"

  depends_on = [aws_glue_data_catalog_encryption_settings.catalog_encryption]
}


resource "aws_glue_catalog_table" "glue_encrypted_table" {
  name          = "glue_encrypted_table"
  database_name = aws_glue_catalog_database.glue_encrypted_database.name
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

    location = "s3://${aws_s3_bucket.brunoluz_teste_kms.bucket}/glue_encrypted_table/"

    input_format  = "org.apache.hadoop.hive.ql.io.avro.AvroContainerInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat"

    ser_de_info {
      name                  = "avro_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.avro.AvroSerDe"
      parameters            = {}
    }
  }
}

