resource "aws_s3_bucket" "brunoluz_teste_kms" {
  bucket        = "brunoluz-teste-kms"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "brunoluz_teste_kms" {
  bucket = aws_s3_bucket.brunoluz_teste_kms.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.kms_glue_catalog.arn
    }
  }
}

resource "aws_s3_object" "arquivo_txt" {
  bucket  = aws_s3_bucket.brunoluz_teste_kms.id
  key     = "arquivo.txt"
  content = "brunoluz"
}
