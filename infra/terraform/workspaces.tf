# Terraform Workspaces for Multi-Environment

terraform {
  required_version = ">= 1.5"
  backend "s3" {}
}

# Workspace-specific configurations
locals {
  workspace_configs = {
    dev = {
      region                  = "us-east-1"
      cluster_name           = "convocatorias-dev"
      node_count             = 2
      instance_type          = "t3.small"
      min_replicas           = 1
      max_replicas           = 3
      sampling_rate         = 1.0
      chaos_enabled          = false
    }
    staging = {
      region                  = "us-east-1"
      cluster_name           = "convocatorias-staging"
      node_count             = 3
      instance_type          = "t3.medium"
      min_replicas           = 2
      max_replicas           = 5
      sampling_rate         = 0.5
      chaos_enabled          = true
    }
    prod = {
      region                  = "us-east-1"
      cluster_name           = "convocatorias-prod"
      node_count             = 5
      instance_type          = "t3.large"
      min_replicas           = 3
      max_replicas           = 10
      sampling_rate         = 0.1
      chaos_enabled          = true
    }
  }
}

# Get workspace configuration
locals {
  config = local.workspace_configs[terraform.workspace]
}

# Variables using workspace values
variable "region" {
  default = local.config.region
}

variable "cluster_name" {
  default = local.config.cluster_name
}

variable "sampling_rate" {
  default = local.config.sampling_rate
}

# Provider aliases for multi-cloud
provider "aws" {
  alias  = "primary"
  region = var.primary_region
}

provider "aws" {
  alias  = "secondary"
  region = var.secondary_region
}

provider "azurerm" {
  features {}
}

# Multi-cluster deployment
module "eks_primary" {
  source = "./modules/eks"
  providers = {
    aws = aws.primary
  }
  cluster_name = "${local.config.cluster_name}-primary"
  node_count   = local.config.node_count
  instance_type = local.config.instance_type
}