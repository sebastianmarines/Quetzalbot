data "aws_availability_zones" "available" {}
data "aws_ecrpublic_authorization_token" "token" {}
data "aws_region" "current" {}

resource "aws_iam_policy" "alb" {
  name        = "ALBIngressControllerIAMPolicy"
  description = "IAM policy for ALB Ingress Controller"
  policy      = file("${path.module}/policies/alb-ingress-controller.json")
}

resource "aws_iam_policy" "alb_2" {
  name   = "ALBIngressControllerIAMPolicy2"
  policy = file("${path.module}/policies/iam_policy.json")
}

resource "aws_iam_policy" "route53" {
  name   = "Route53Policy"
  policy = file("${path.module}/policies/route53.json")
}

resource "aws_iam_policy" "ses" {
  name = "SESPolicy"
  policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = [
            "ses:SendEmail",
            "ses:SendRawEmail",
            "ses:SendTemplatedEmail",
          ]
          Resource = "*"
        },
      ]
    }
  )
}

module "vpc_cni_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name_prefix      = "VPC-CNI-IRSA"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.13.1"

  cluster_name    = local.name
  cluster_version = "1.30"

  enable_cluster_creator_admin_permissions = true
  cluster_endpoint_public_access           = true

  cluster_addons = {
    coredns                = {}
    eks-pod-identity-agent = {}
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent              = true
      before_compute           = true
      service_account_role_arn = module.vpc_cni_irsa.iam_role_arn
      configuration_values = jsonencode({
        env = {
          # Reference docs https://docs.aws.amazon.com/eks/latest/userguide/cni-increase-ip-addresses.html
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET       = "1"
        }
      })
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  iam_role_additional_policies = {
    additional = aws_iam_policy.alb.arn
    additional = aws_iam_policy.alb_2.arn
    additional = aws_iam_policy.route53.arn
  }

  eks_managed_node_groups = {
    karpenter = {
      instance_types = ["m7a.medium"]

      min_size     = 1
      max_size     = 2
      desired_size = 2

      iam_role_additional_policies = {
        AmazonSSMManagedInstanceCore  = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
        ALBIngressControllerIAMPolicy = aws_iam_policy.alb.arn
        Route53Policy                 = aws_iam_policy.route53.arn
        SESPolicy                     = aws_iam_policy.ses.arn
      }

#      taints = {
#        addons = {
#          key    = "CriticalAddonsOnly"
#          value  = "true"
#          effect = "NO_SCHEDULE"
#        },
#      }
    }
  }

  node_security_group_tags = {
    "kubernetes.io/cluster/${local.name}" = null
  }

  tags = {
    "karpenter.sh/discovery" = local.name
  }
}

################################################################################
# Karpenter
################################################################################

module "karpenter" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "20.13.1"

  cluster_name = module.eks.cluster_name

  enable_pod_identity             = true
  create_pod_identity_association = true

  node_iam_role_additional_policies = {
    AmazonSSMManagedInstanceCore  = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    ALBIngressControllerIAMPolicy = aws_iam_policy.alb.arn
    Route53Policy                 = aws_iam_policy.route53.arn
    SESPolicy                     = aws_iam_policy.ses.arn
  }
}

module "karpenter_disabled" {
  source  = "terraform-aws-modules/eks/aws//modules/karpenter"
  version = "20.13.1"

  create = false
}

################################################################################
# Karpenter Helm chart & manifests
# Not required; just to demonstrate functionality of the sub-module
################################################################################

resource "helm_release" "karpenter" {
  namespace           = "kube-system"
  name                = "karpenter"
  repository          = "oci://public.ecr.aws/karpenter"
  repository_username = data.aws_ecrpublic_authorization_token.token.user_name
  repository_password = data.aws_ecrpublic_authorization_token.token.password
  chart               = "karpenter"
  version             = "0.37.0"
  wait                = false

  values = [
    <<-EOT
    settings:
      clusterName: ${module.eks.cluster_name}
      clusterEndpoint: ${module.eks.cluster_endpoint}
      interruptionQueue: ${module.karpenter.queue_name}
    EOT
  ]

  depends_on = [helm_release.alb_ingress_controller]
}

resource "kubectl_manifest" "karpenter_node_class" {
  yaml_body = <<-YAML
    apiVersion: karpenter.k8s.aws/v1beta1
    kind: EC2NodeClass
    metadata:
      name: default
    spec:
      amiFamily: AL2023
      role: ${module.karpenter.node_iam_role_name}
      subnetSelectorTerms:
        - tags:
            karpenter.sh/discovery: ${module.eks.cluster_name}
      securityGroupSelectorTerms:
        - tags:
            karpenter.sh/discovery: ${module.eks.cluster_name}
      tags:
        karpenter.sh/discovery: ${module.eks.cluster_name}
  YAML

  depends_on = [
    helm_release.karpenter
  ]
}

resource "kubectl_manifest" "karpenter_node_pool" {
  yaml_body = <<-YAML
    apiVersion: karpenter.sh/v1beta1
    kind: NodePool
    metadata:
      name: default
    spec:
      template:
        spec:
          nodeClassRef:
            name: default
          requirements:
            - key: "karpenter.k8s.aws/instance-category"
              operator: In
              values: ["m"]
            - key: "karpenter.k8s.aws/instance-cpu"
              operator: In
              values: ["1"]
            - key: "karpenter.k8s.aws/instance-hypervisor"
              operator: In
              values: ["nitro"]
            - key: "karpenter.k8s.aws/instance-generation"
              operator: Gt
              values: ["6"]
            - key: "kubernetes.io/arch"
              operator: In
              values: ["amd64"]
      limits:
        cpu: 5000
      disruption:
        consolidationPolicy: WhenEmpty
        consolidateAfter: 30s
  YAML

  depends_on = [
    kubectl_manifest.karpenter_node_class
  ]
}

resource "helm_release" "alb_ingress_controller" {
  namespace        = "kube-system"
  name             = "alb-ingress-controller"
  repository       = "https://aws.github.io/eks-charts"
  chart            = "aws-load-balancer-controller"
  create_namespace = true
  wait             = false
  version          = ""

  values = [
    <<-EOT
        clusterName: ${module.eks.cluster_name}
        vpcId: ${module.vpc.vpc_id}
        region: ${data.aws_region.current.name}
#        enableServiceMutatorWebhook: false
        EOT
  ]

  depends_on = [module.karpenter]
}

resource "kubectl_manifest" "external_dns" {
  yaml_body  = file("${path.module}/manifests/external-dns.yaml")
  depends_on = [aws_acm_certificate_validation.cert]
}

resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

resource "helm_release" "argocd" {
  namespace  = kubernetes_namespace.argocd.metadata.0.name
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  depends_on = [helm_release.alb_ingress_controller]
}

resource "kubernetes_namespace" "fenix" {
  metadata {
    name = local.name
  }
}

resource "kubernetes_secret" "db" {
  metadata {
    name      = "${local.name}-db-connection-string"
    namespace = kubernetes_namespace.fenix.metadata.0.name
  }

  data = {
    connection_string = join("", [
      "postgresql://",
      module.db.db_instance_username,
      ":",
      jsondecode(data.aws_secretsmanager_secret_version.master.secret_string)["password"],
      "@",
      module.db.db_instance_endpoint,
      "/",
      local.name
    ])
  }
}
