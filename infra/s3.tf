resource "aws_s3_bucket" "brunoluz_teste_kms" {
  bucket        = "brunoluz-teste-kms"
  force_destroy = true
}
