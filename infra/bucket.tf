resource "aws_s3_bucket" "fenix" {
    bucket                      = "fenix-screenshots-abk1249mx"
    object_lock_enabled         = false
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
                    Resource  = [
                        "arn:aws:s3:::fenix-screenshots-abk1249mx/*",
                        "arn:aws:s3:::fenix-screenshots-abk1249mx",
                    ]
                },
            ]
            Version   = "2012-10-17"
        }
    )
}