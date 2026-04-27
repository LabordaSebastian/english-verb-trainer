terraform {
  required_version = ">= 1.3.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

# Pull the official PostgreSQL 15 image
resource "docker_image" "postgres" {
  name         = "postgres:15"
  keep_locally = true
}

# Create the PostgreSQL container
resource "docker_container" "postgres" {
  name  = var.container_name
  image = docker_image.postgres.image_id

  restart = "unless-stopped"

  ports {
    internal = 5432
    external = var.db_port
  }

  env = [
    "POSTGRES_DB=${var.db_name}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]

  # Persist data across container restarts
  volumes {
    volume_name    = docker_volume.postgres_data.name
    container_path = "/var/lib/postgresql/data"
  }

  healthcheck {
    test         = ["CMD-SHELL", "pg_isready -U ${var.db_user} -d ${var.db_name}"]
    interval     = "10s"
    timeout      = "5s"
    retries      = 5
    start_period = "10s"
  }
}

# Persistent volume so data survives container restarts
resource "docker_volume" "postgres_data" {
  name = "english_trainer_pgdata"
}
