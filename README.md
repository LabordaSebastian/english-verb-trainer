# English Irregular Verb Trainer — DevOps Edition

Quiz de verbos irregulares en inglés con stack DevOps real.

## 🛠️ Stack

| Capa | Tecnología |
|---|---|
| CLI | Python + Typer |
| Base de datos | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| Infraestructura | Terraform (Docker Provider) |
| Contenedor | Docker |
| Tests | pytest |

---

## 🚀 Quick Start

### 1. Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / Mac / Linux)
- [Terraform CLI](https://developer.hashicorp.com/terraform/install)
- Python 3.10+

### 2. Levantar PostgreSQL con Terraform

```bash
cd terraform
terraform init
terraform apply -auto-approve
cd ..
```

### 3. Configurar variables de entorno

```bash
# Linux / Mac
cp .env.example .env

# Windows PowerShell
Copy-Item .env.example .env
```

### 4. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 5. Cargar los 50 verbos irregulares

```bash
python main.py seed
```

### 6. ¡A practicar!

```bash
# Quiz aleatorio (10 preguntas por defecto)
python main.py quiz

# Practicar un verbo específico
python main.py quiz --verb read

# Quiz largo
python main.py quiz --rounds 20

# Ver tu progreso
python main.py stats
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

> Los tests usan SQLite en memoria — **no requieren Postgres ni Docker**.

---

## 🔥 Ejemplo de sesión

```
╔══════════════════════════════════════════════╗
║   🎯  English Irregular Verb Trainer         ║
║       DevOps Edition  |  PostgreSQL + TF     ║
╚══════════════════════════════════════════════╝

  Starting quiz — 10 question(s). Type 'q' to quit.

  Question 1/10
  Base verb:  READ
  Type the  Past Tense  and  Past Participle  separated by a space.
  Your answer: read read

  ✅  Correct!  READ → read → read
────────────────────────────────────────────────
  Question 2/10
  Base verb:  GO
  Your answer: went go

  ❌  Wrong!    GO → went → gone
             You answered: went → go
────────────────────────────────────────────────

  📊  Result: 1/2 correct (50.0%)
```

---

## 🏗️ Infraestructura con Terraform

Terraform usa el [Docker Provider](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs)
para levantar un contenedor PostgreSQL 15 localmente con volumen persistente.

```bash
# Ver qué va a crear
terraform -chdir=terraform plan

# Levantar
terraform -chdir=terraform apply -auto-approve

# Ver la connection string
terraform -chdir=terraform output database_url

# Destruir (elimina el contenedor pero NO los datos del volumen)
terraform -chdir=terraform destroy
```
