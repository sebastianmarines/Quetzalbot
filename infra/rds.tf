module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = local.name

  engine            = "postgres"
  engine_version    = "16.3"
  instance_class    = "db.t4g.medium"
  allocated_storage = 5
  family = "postgres16"

  db_name  = local.name
  username = local.name
  port     = "3306"

  create_db_subnet_group = true
  subnet_ids             = module.vpc.private_subnets

  manage_master_user_password = true
}