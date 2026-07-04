# Cloud Provider Selection
variable "cloud_provider" {
  description = "Cloud provider to use: aws, azure, or gcp"
  type        = string
  default     = "aws"
  validation {
    condition     = contains(["aws", "azure", "gcp"], var.cloud_provider)
    error_message = "Cloud provider must be aws, azure, or gcp"
  }
}

# AWS Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "eks_cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "convocatorias-prod"
}

variable "eks_node_size" {
  description = "EKS node instance size"
  type        = string
  default     = "t3.medium"
}

variable "eks_node_count" {
  description = "EKS initial node count"
  type        = number
  default     = 2
}

variable "mysql_instance_class" {
  description = "MySQL instance class"
  type        = string
  default     = "db.t4g.micro"
}

# Azure Variables
variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "aks_node_count" {
  description = "AKS node count"
  type        = number
  default     = 2
}

# GCP Variables
variable "gcp_project" {
  description = "GCP project ID"
  type        = string
  default     = ""
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

# Database Variables
variable "mysql_name" {
  description = "MySQL database name"
  type        = string
  default     = "convocatorias-db"
}

variable "mysql_username" {
  description = "MySQL administrator username"
  type        = string
  default     = "admin"
}

variable "environment" {
  description = "Environment: dev, staging, prod"
  type        = string
  default     = "prod"
}

# Tags
variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "convocatorias-automatizacion"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}