variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "english_trainer"
}

variable "db_user" {
  description = "PostgreSQL user"
  type        = string
  default     = "trainer_user"
}

variable "db_password" {
  description = "PostgreSQL password"
  type        = string
  default     = "trainer_pass_2024"
  sensitive   = true
}

variable "db_port" {
  description = "Host port to expose PostgreSQL"
  type        = number
  default     = 5432
}

variable "container_name" {
  description = "Name for the Docker container"
  type        = string
  default     = "english_trainer_db"
}
