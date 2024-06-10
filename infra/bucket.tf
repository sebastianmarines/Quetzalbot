resource "random_string" "random" {
  length  = 8
  special = false
  numeric = false
  upper   = false
}

resource "aws_s3_bucket" "fenix" {
  bucket              = "fenix-screenshots-${random_string.random.result}"
  object_lock_enabled = false
}

resource "aws_s3_bucket_policy" "fenix" {
  bucket = aws_s3_bucket.fenix.bucket
  policy = jsonencode(
    {
      Statement = [
        {
          Action    = "s3:GetObject"
          Effect    = "Allow"
          Principal = "*"
          Resource = [
            "arn:aws:s3:::${aws_s3_bucket.fenix.bucket}/*",
            "arn:aws:s3:::${aws_s3_bucket.fenix.bucket}",
          ]
        },
      ]
      Version = "2012-10-17"
    }
  )

  depends_on = [aws_s3_bucket_public_access_block.fenix]
}

resource "aws_s3_bucket_public_access_block" "fenix" {
  bucket = aws_s3_bucket.fenix.bucket

  block_public_acls   = false
  block_public_policy = false
}