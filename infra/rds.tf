module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = local.name

  engine            = "postgres"
  engine_version    = "16.3"
  instance_class    = "db.t4g.medium"
  allocated_storage = 5
  family            = "postgres16"

  db_name  = local.name
  username = local.name
  port     = "3306"

  create_db_subnet_group = true
  subnet_ids             = module.vpc.private_subnets

  manage_master_user_password = true
  vpc_security_group_ids      = [module.db_sg.security_group_id]
}

module "db_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.2"

  name   = "${local.name}-db"
  vpc_id = module.vpc.vpc_id
  ingress_with_source_security_group_id = [
    {
      from_port                = module.db.db_instance_port
      to_port                  = module.db.db_instance_port
      protocol                 = "tcp"
      description              = "PostgreSQL"
      source_security_group_id = module.eks.node_security_group_id
    }
  ]
}