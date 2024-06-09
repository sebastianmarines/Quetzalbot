resource "aws_ecr_repository" "fenix" {
  name         = local.name
  force_delete = true
}