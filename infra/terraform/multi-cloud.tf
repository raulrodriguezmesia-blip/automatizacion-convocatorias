# Multi-cloud EKS and AKS Configuration

# AWS EKS Cluster (US-East)
module "eks_primary" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  providers = {
    aws = aws.primary
  }

  cluster_name    = "convocatorias-primary"
  cluster_version = "1.29"
  
  vpc_id     = module.vpc_primary.vpc_id
  subnet_ids = module.vpc_primary.private_subnets

  eks_managed_node_groups = {
    primary_nodes = {
      min_size     = 3
      max_size     = 10
      desired_size = 3
      instance_types = ["t3.medium"]
    }
  }
}

# Azure AKS Cluster (East US)
module "aks_secondary" {
  source  = "Azure/aks/azure//modules/aks"
  version = "~> 6.0"
  
  resource_group_name = "convocatorias-rg-secondary"
  cluster_name        = "convocatorias-aks-secondary"
  location            = "East US"
  
  agent_pool_profiles = [
    {
      name                = "nodepool"
      count               = 3
      vm_size             = "Standard_D2s_v3"
      vnet_subnet_id      = module.vnet_secondary.aks_subnet_id
    }
  ]
}

# Multi-cluster Istio configuration
resource "kubernetes_config_map" "istio_multi_cluster" {
  metadata {
    name = "istio-multicluster-config"
    namespace = "istio-system"
  }
  data = {
    "primary_cluster_endpoint" = module.eks_primary.cluster_endpoint
    "secondary_cluster_endpoint" = module.aks_secondary.aks_kube_config
    "mesh_network" = yamlencode({
      networks = {
        primary = {
          endpoints = [module.eks_primary.cluster_endpoint]
        }
        secondary = {
          endpoints = [module.aks_secondary.aks_kube_config]
        }
      }
    })
  }
}

# Failover routing with Istio
resource "kubectl_manifest" "multicluster_failover" {
  yaml_body = yamlencode({
    apiVersion = "networking.istio.io/v1beta1"
    kind = "ServiceEntry"
    metadata = {
      name = "convocatorias-failover"
    }
    spec = {
      hosts = ["convocatorias-api.backup"]
      location = "MESH_EXTERNAL"
      ports = [{
        number = 80
        name = http
        protocol = "HTTP"
      }]
      resolution = "DNS"
      endpoints = [{
        address = module.aks_secondary.aks_private_fqdn
        locality = "eastus"
      }]
    }
  })
}