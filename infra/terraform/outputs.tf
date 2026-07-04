# Cluster endpoints
output "eks_endpoint" {
  value = var.cloud_provider == "aws" ? aws_eks_cluster.main[0].endpoint : null
}

output "aks_kubeconfig" {
  value = var.cloud_provider == "azure" ? azurerm_kubernetes_cluster.main[0].kube_config_raw : null
  sensitive = true
}

output "gke_endpoint" {
  value = var.cloud_provider == "gcp" ? google_container_cluster.main[0].endpoint : null
}

# Database connection info
output "mysql_endpoint" {
  value = var.cloud_provider == "aws" ? aws_db_instance.mysql[0].endpoint : null
}

output "azure_mysql_fqdn" {
  value = var.cloud_provider == "azure" ? azurerm_mysql_flexible_server.main[0].fqdn : null
}

output "gcp_mysql_connection_name" {
  value = var.cloud_provider == "gcp" ? google_sql_database_instance.mysql[0].connection_name : null
}

# Storage for attachments
output "s3_bucket_name" {
  value = var.cloud_provider == "aws" ? aws_s3_bucket.attachments[0].bucket : null
}

output "azure_storage_account" {
  value = var.cloud_provider == "azure" ? azurerm_storage_account.main[0].name : null
}

# Container image
output "container_image" {
  value = "ghcr.io/${var.github_repository}/convocatorias:${var.environment}"
}