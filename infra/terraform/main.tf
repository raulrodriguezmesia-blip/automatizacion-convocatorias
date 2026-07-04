# Backend Configuration (remote state)
terraform {
  backend "s3" {
    bucket         = "convocatorias-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "convocatorias-terraform-locks"
    encrypt        = true
  }
}

# AWS EKS Cluster
resource "aws_vpc" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  cidr_block = "10.0.0.0/16"
  tags = var.tags
}

resource "aws_subnet" "private" {
  count = var.cloud_provider == "aws" ? 2 : 0
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = cidrsubnet(aws_vpc.main[0].cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = var.tags
}

resource "aws_eks_cluster" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.eks[0].arn
  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
  depends_on = [aws_iam_role_policy_attachment.cluster]
}

resource "aws_eks_node_group" "main" {
  count = var.cloud_provider == "aws" ? 1 : 0
  cluster_name    = aws_eks_cluster.main[0].name
  node_group_name = "convocatorias-nodes"
  node_role_arn   = aws_iam_role.nodes[0].arn
  subnet_ids      = aws_subnet.private[*].id
  instance_types  = [var.eks_node_size]
  scaling_config {
    desired_size = var.eks_node_count
    min_size     = 2
    max_size     = 10
  }
}

# Azure AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  name                = "convocatorias-aks"
  location            = var.azure_location
  resource_group_name = azurerm_resource_group.main[0].name
  dns_prefix          = "convocatorias"
  default_node_pool {
    name       = "default"
    node_count = var.aks_node_count
    vm_size    = "Standard_D2s_v3"
  }
  identity {
    type = "SystemAssigned"
  }
}

# GCP GKE Cluster
resource "google_container_cluster" "main" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  name     = "convocatorias-gke"
  location = var.gcp_region
  initial_node_count = 2
  node_config {
    machine_type = "e2-medium"
  }
}

# MySQL RDS (AWS)
resource "aws_db_instance" "mysql" {
  count = var.cloud_provider == "aws" ? 1 : 0
  identifier     = "convocatorias-mysql"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = var.mysql_instance_class
  allocated_storage = 20
  username       = var.mysql_username
  password       = random_password.mysql.result
  vpc_security_group_ids = [aws_security_group.mysql[0].id]
  db_subnet_group_name = aws_db_subnet_group.main[0].name
  skip_final_snapshot = true
}

# Azure Database for MySQL
resource "azurerm_mysql_flexible_server" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  name                = "convocatorias-mysql"
  location            = var.azure_location
  resource_group_name = azurerm_resource_group.main[0].name
  sku_name            = "B_Gen5_1"
  administrator_login = var.mysql_username
  administrator_login_password = random_password.mysql.result
}

# GCP Cloud SQL for MySQL
resource "google_sql_database_instance" "mysql" {
  count = var.cloud_provider == "gcp" ? 1 : 0
  name             = "convocatorias-mysql"
  database_version = "MYSQL_8_0"
  settings {
    tier = "db-f1-micro"
  }
}

# Azure Storage Account (para adjuntos)
resource "azurerm_storage_account" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  name                     = "convocatoriasstorage"
  resource_group_name      = azurerm_resource_group.main[0].name
  location                 = var.azure_location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# AWS S3 Bucket (para adjuntos)
resource "aws_s3_bucket" "attachments" {
  count = var.cloud_provider == "aws" ? 1 : 0
  bucket = "convocatorias-attachments-${var.environment}"
  acl    = "private"
}

# Azure Resource Group
resource "azurerm_resource_group" "main" {
  count = var.cloud_provider == "azure" ? 1 : 0
  name     = "convocatorias-rg"
  location = var.azure_location
}

# IAM Roles (AWS)
resource "aws_iam_role" "eks" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name = "eks-cluster-role"
  assume_role_policy = data.aws_iam_policy_document.cluster_assume[0].json
}

resource "aws_iam_role" "nodes" {
  count = var.cloud_provider == "aws" ? 1 : 0
  name = "eks-node-role"
  assume_role_policy = data.aws_iam_policy_document.nodes_assume[0].json
}

resource "random_password" "mysql" {
  length  = 16
  special = true
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_iam_policy_document" "cluster_assume" {
  count = var.cloud_provider == "aws" ? 1 : 0
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}