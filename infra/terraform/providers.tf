terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.endpoint[0].endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.certificate[0].data)
  token                  = data.aws_eks_cluster_auth.token[0]
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.endpoint[0].endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.certificate[0].data)
    token                  = data.aws_eks_cluster_auth.token[0]
  }
}