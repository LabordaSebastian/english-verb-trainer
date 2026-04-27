output "database_url" {
  description = "SQLAlchemy-compatible connection string for the PostgreSQL database"
  value       = "postgresql://${var.db_user}:${var.db_password}@localhost:${var.db_port}/${var.db_name}"
  sensitive   = true
}

output "container_name" {
  description = "Name of the running Docker container"
  value       = docker_container.postgres.name
}

output "container_id" {
  description = "Docker container ID"
  value       = docker_container.postgres.id
}
