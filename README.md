# 🎯 English Irregular Verb Trainer — DevOps Edition

> Aplicación de línea de comandos para practicar verbos irregulares en inglés, construida con un stack de herramientas reales de DevOps: Python, PostgreSQL, Terraform y GitHub Actions.

[![CI](https://github.com/LabordaSebastian/english-verb-trainer/actions/workflows/ci.yml/badge.svg)](https://github.com/LabordaSebastian/english-verb-trainer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Terraform](https://img.shields.io/badge/Terraform-1.3%2B-7B42BC?logo=terraform)](https://www.terraform.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 ¿Qué hace esta aplicación?

El programa te pregunta un verbo en inglés en su forma base (por ejemplo **READ**) y vos tenés que responder con el **pasado simple** y el **participio pasado**, separados por un espacio:

```
Base verb:  READ
Your answer: > read read

✅  Correct!  READ → read → read
```

Si la respuesta es incorrecta, te muestra cuál era la forma correcta:

```
Base verb:  GO
Your answer: > goed gone

❌  Wrong!    GO → went → gone
             You answered: goed → gone
```

Al final de cada sesión ves tu porcentaje de aciertos, y con el comando `stats` podés ver qué verbos te están costando más.

---

## 🛠️ Stack Tecnológico

Este proyecto usa herramientas del mundo real de DevOps. A continuación se explica cada una, para qué sirve y por qué fue elegida.

---

### 🐍 Python 3.10+

**¿Qué es?**
Python es uno de los lenguajes más utilizados en DevOps, automatización e infraestructura. Herramientas como Ansible, AWS CLI y muchos scripts de CI/CD están escritos en Python.

**¿Para qué se usa acá?**
Es el lenguaje principal de la aplicación. Contiene toda la lógica del quiz, la conexión a la base de datos y la interfaz de línea de comandos.

**¿Por qué Python?**
- Es el estándar en el mundo DevOps para scripting y automatización.
- Compatible con Windows, Linux y Mac sin modificaciones.
- Tiene un ecosistema enorme de librerías listas para usar.

---

### ⌨️ Typer

**¿Qué es?**
[Typer](https://typer.tiangolo.com/) es una librería de Python para construir interfaces de línea de comandos (CLI) modernas. Está construida sobre Click, que es la herramienta CLI más usada en el ecosistema Python.

**¿Para qué se usa acá?**
Define los comandos de la aplicación:
- `python main.py quiz` — inicia el quiz
- `python main.py seed` — carga los verbos en la base de datos
- `python main.py stats` — muestra el progreso del usuario

**¿Por qué Typer?**
- Genera automáticamente el `--help` de cada comando.
- Permite agregar opciones como `--verb read` o `--rounds 20` de forma simple.
- Es el estándar moderno para CLIs en Python.

```bash
# Ejemplos de uso con opciones
python main.py quiz --verb go        # practica solo el verbo GO
python main.py quiz --rounds 20      # quiz de 20 preguntas
python main.py stats                 # ver tu progreso
```

---

### 🐘 PostgreSQL 15

**¿Qué es?**
[PostgreSQL](https://www.postgresql.org/) es uno de los motores de base de datos relacionales más populares y robustos del mundo. Es ampliamente utilizado en producción por empresas de todo tamaño.

**¿Para qué se usa acá?**
Almacena dos tablas:

| Tabla | Contenido |
|---|---|
| `verbs` | Los 50 verbos irregulares (base, pasado, participio, formas alternativas) |
| `user_attempts` | Cada intento del usuario: qué respondió, si fue correcto, y cuándo |

Gracias a `user_attempts`, la aplicación puede mostrarte estadísticas reales: cuántos aciertos tuviste, cuál es tu precisión y qué verbos te cuestan más.

**¿Por qué PostgreSQL y no un archivo JSON o SQLite?**
- En un entorno DevOps real, los datos viven en una base de datos con motor, no en archivos planos.
- PostgreSQL permite escalar: mañana podés agregar múltiples usuarios, un backend REST, un dashboard, etc.
- Practicar con PostgreSQL te prepara para el mundo real.

---

### 🔗 SQLAlchemy 2.0

**¿Qué es?**
[SQLAlchemy](https://www.sqlalchemy.org/) es el ORM (Object-Relational Mapper) más utilizado en Python. Permite interactuar con bases de datos SQL usando objetos Python en lugar de escribir SQL crudo.

**¿Para qué se usa acá?**
Define los modelos de datos (`Verb`, `UserAttempt`) y maneja todas las consultas a PostgreSQL: insertar verbos, registrar intentos, calcular estadísticas.

**¿Por qué SQLAlchemy?**
- Abstrae el SQL: el código Python funciona igual si mañana cambiás de PostgreSQL a MySQL u otro motor.
- Los tests unitarios usan SQLite en memoria (sin necesidad de levantar Postgres) gracias a esta abstracción.
- Es el estándar de la industria Python para interactuar con bases de datos.

---

### 🏗️ Terraform

**¿Qué es?**
[Terraform](https://www.terraform.io/) es la herramienta de **Infrastructure as Code (IaC)** más usada en DevOps. Permite definir infraestructura (servidores, bases de datos, redes, contenedores) como archivos de código, y luego crearla o destruirla con un comando.

**¿Para qué se usa acá?**
Aprovisiona el contenedor de PostgreSQL usando el **Docker Provider** de Terraform. En lugar de ejecutar `docker run` manualmente, Terraform declara el estado deseado y lo ejecuta:

```hcl
# terraform/main.tf
resource "docker_container" "postgres" {
  name  = "english_trainer_db"
  image = "postgres:15"
  ...
}
```

**Comandos Terraform en este proyecto:**
```bash
terraform init            # descarga el provider Docker
terraform plan            # muestra qué va a crear (sin ejecutar)
terraform apply           # crea el contenedor PostgreSQL
terraform destroy         # elimina el contenedor
terraform output          # muestra el DATABASE_URL generado
```

**¿Por qué Terraform?**
- Es la herramienta IaC estándar en la industria (AWS, GCP, Azure, Docker...).
- El estado de la infraestructura queda documentado en código versionable con Git.
- Practicar Terraform con Docker local es exactamente lo mismo que usarlo para crear recursos en la nube.

---

### 🐳 Docker

**¿Qué es?**
[Docker](https://www.docker.com/) es la plataforma de contenedores más utilizada en DevOps. Permite empaquetar aplicaciones con todas sus dependencias en una imagen portable que corre igual en cualquier máquina.

**¿Para qué se usa acá?**
Dos usos:

1. **Contenedor de PostgreSQL**: Terraform levanta un contenedor oficial `postgres:15`. Así no tenés que instalar PostgreSQL en tu máquina — Docker lo aísla completamente.

2. **Imagen de la app**: El `Dockerfile` empaqueta la aplicación Python para que cualquiera pueda correrla sin instalar Python ni dependencias:
   ```bash
   docker run -it ghcr.io/labordaSebastian/english-verb-trainer quiz
   ```

**¿Por qué Docker?**
- Elimina el clásico problema de "en mi máquina funciona".
- Permite distribuir la app fácilmente a través de GitHub Container Registry (GHCR).

---

### ⚙️ GitHub Actions (CI/CD)

**¿Qué es?**
[GitHub Actions](https://github.com/features/actions) es la plataforma de **CI/CD** integrada en GitHub. Permite automatizar tareas (tests, builds, deploys) cada vez que se sube código al repositorio.

**¿Para qué se usa acá?**
Este proyecto tiene dos workflows:

#### 🔵 CI — Continuous Integration (`.github/workflows/ci.yml`)

Se ejecuta automáticamente en cada **push** y **pull request** a `main`.

| Job | Herramienta | ¿Qué hace? |
|---|---|---|
| `lint` | **ruff** | Verifica que el código sigue las convenciones de estilo Python |
| `test` | **pytest** | Corre los 18 tests unitarios en Python 3.10, 3.11 y 3.12 |

Si algún test falla, el push queda marcado en rojo en GitHub — nadie puede mergear código roto.

#### 🟢 CD — Continuous Delivery (`.github/workflows/cd.yml`)

Se ejecuta cuando se crea un **tag de versión** (ej: `v1.0.0`):

```bash
git tag v1.0.0
git push origin v1.0.0
```

Automáticamente hace:
1. ✅ Corre los tests
2. 🐳 Buildea la imagen Docker y la publica en **GitHub Container Registry (GHCR)**
3. 📦 Crea un **GitHub Release** con changelog automático generado a partir de los commits

**¿Por qué CI/CD?**
- Garantiza que el código siempre está testeado antes de que llegue a producción.
- Automatiza el proceso de release: un tag = una versión publicada, sin pasos manuales.
- Es el flujo estándar en cualquier equipo de desarrollo moderno.

---

### 🧪 pytest

**¿Qué es?**
[pytest](https://pytest.org/) es el framework de testing más usado en Python. Permite escribir y correr tests unitarios de forma simple y con reportes claros.

**¿Para qué se usa acá?**
El proyecto tiene **18 tests** que cubren:
- Validación de respuestas correctas e incorrectas (mayúsculas, minúsculas, formas alternativas)
- Búsqueda de verbos por nombre
- Registro de intentos en la base de datos
- Cálculo de estadísticas del usuario

**Clave de diseño**: los tests usan **SQLite en memoria** (no PostgreSQL). Esto significa que los tests son instantáneos y no necesitan Docker ni Terraform para correr — ideal para CI.

```bash
pytest tests/ -v
# 18 passed in 0.97s ✅
```

---

### 🔍 ruff

**¿Qué es?**
[ruff](https://docs.astral.sh/ruff/) es un linter de Python extremadamente rápido (escrito en Rust). Reemplaza herramientas como flake8, isort y pycodestyle en una sola herramienta.

**¿Para qué se usa acá?**
Verifica que el código sigue las convenciones de estilo de Python (PEP 8) antes de que llegue a `main`. Se ejecuta en el pipeline de CI.

---

## 📁 Estructura del Proyecto

```
english-verb-trainer/
│
├── 📄 main.py                  # Entry point CLI — define los comandos quiz/seed/stats
├── 🚀 start.py                 # Launcher automático — un solo comando para arrancar todo
├── 🐳 Dockerfile               # Imagen Docker de la aplicación
├── 📋 Makefile                 # Comandos DevOps (make quiz, make test, etc.)
├── 📦 requirements.txt         # Dependencias Python
├── ⚙️ pyproject.toml           # Configuración del proyecto Python
├── 🔒 .env.example             # Variables de entorno de ejemplo
├── 🙈 .gitignore               # Archivos excluidos de Git
│
├── app/                        # Código fuente de la aplicación
│   ├── database.py             # Conexión SQLAlchemy a PostgreSQL
│   ├── models.py               # Tablas: Verb y UserAttempt
│   ├── quiz.py                 # Lógica: validación, estadísticas
│   └── seed.py                 # 50 verbos irregulares precargados
│
├── terraform/                  # Infraestructura como código
│   ├── main.tf                 # Contenedor PostgreSQL 15 vía Docker Provider
│   ├── variables.tf            # Variables: nombre DB, usuario, contraseña, puerto
│   └── outputs.tf              # Output: DATABASE_URL lista para usar
│
├── tests/                      # Tests unitarios
│   └── test_quiz.py            # 18 tests con SQLite en memoria
│
└── .github/
    └── workflows/
        ├── ci.yml              # CI: lint + pytest en cada push
        └── cd.yml              # CD: Docker image + Release en cada tag
```

---

## 🚀 Cómo usar el proyecto

### Prerequisitos

| Herramienta | Instalación |
|---|---|
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) |
| **Docker Desktop** | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Terraform CLI** | [developer.hashicorp.com/terraform/install](https://developer.hashicorp.com/terraform/install) |

### ⚡ Arranque en un solo comando

```bash
# Clona el repositorio
git clone https://github.com/LabordaSebastian/english-verb-trainer.git
cd english-verb-trainer

# Lanza todo automáticamente
python start.py
```

El script `start.py` hace todo por vos:
1. Verifica que Docker esté corriendo
2. Verifica que Terraform esté instalado
3. Levanta el contenedor PostgreSQL con `terraform apply`
4. Crea el entorno virtual Python (`.venv`)
5. Instala las dependencias (`pip install`)
6. Copia el archivo `.env`
7. Carga los 50 verbos irregulares en la DB
8. Lanza el quiz 🎯

### Comandos disponibles

```bash
# Iniciar quiz aleatorio (10 preguntas)
python main.py quiz

# Practicar un verbo específico
python main.py quiz --verb read

# Quiz más largo
python main.py quiz --rounds 20

# Ver tu progreso y verbos más difíciles
python main.py stats

# Recargar los verbos en la DB
python main.py seed
```

### Comandos con Makefile (Linux/Mac)

```bash
make quiz      # inicia el quiz
make test      # corre los 18 tests
make lint      # verifica el estilo del código
make destroy   # detiene y elimina el contenedor Postgres
make clean     # elimina el entorno virtual y caché
make help      # muestra todos los comandos disponibles
```

---

## 🔄 Flujo CI/CD

```
Push a main / PR
      │
      ▼
┌─────────────────────────┐
│  CI Workflow             │
│  1. ruff (lint)          │
│  2. pytest × 3 versiones │
│     Python 3.10/11/12   │
└─────────────────────────┘
      │ ✅ todo verde
      ▼
  Merge a main

git tag v1.0.0 && git push --tags
      │
      ▼
┌─────────────────────────────────────┐
│  CD Workflow                         │
│  1. pytest (verificación final)      │
│  2. Build imagen Docker              │
│  3. Push a GHCR                      │
│     ghcr.io/labordaSebastian/...     │
│  4. GitHub Release con changelog     │
└─────────────────────────────────────┘
```

### Correr la app desde Docker (sin instalar Python)

Una vez publicada la imagen, cualquier persona puede correr la app así:

```bash
# Primero levantá Postgres (con Terraform o Docker Compose)
# Luego:
docker run -it --rm \
  --env DATABASE_URL=postgresql://trainer_user:trainer_pass_2024@host.docker.internal:5432/english_trainer \
  ghcr.io/labordaSebastian/english-verb-trainer:latest quiz
```

---

## 🧪 Tests

Los tests corren **sin necesidad de PostgreSQL ni Docker** — usan SQLite en memoria:

```bash
# Activar el entorno virtual primero
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows PowerShell

# Correr los tests
pytest tests/ -v
```

```
tests/test_quiz.py::TestVerbCheckAnswer::test_correct_lowercase      PASSED
tests/test_quiz.py::TestVerbCheckAnswer::test_correct_uppercase      PASSED
tests/test_quiz.py::TestVerbCheckAnswer::test_alt_form_accepted      PASSED
...
======================== 18 passed in 0.97s ============================
```

---

## 📚 Los 50 Verbos Irregulares

| Base | Pasado | Participio |
|---|---|---|
| be | was/were | been |
| have | had | had |
| do | did | done |
| go | went | gone |
| say | said | said |
| get | got | gotten / got |
| make | made | made |
| know | knew | known |
| think | thought | thought |
| take | took | taken |
| see | saw | seen |
| come | came | come |
| give | gave | given |
| find | found | found |
| tell | told | told |
| feel | felt | felt |
| become | became | become |
| leave | left | left |
| put | put | put |
| mean | meant | meant |
| keep | kept | kept |
| let | let | let |
| begin | began | begun |
| show | showed | shown / showed |
| hear | heard | heard |
| run | ran | run |
| bring | brought | brought |
| write | wrote | written |
| sit | sat | sat |
| stand | stood | stood |
| lose | lost | lost |
| pay | paid | paid |
| meet | met | met |
| set | set | set |
| lead | led | led |
| understand | understood | understood |
| speak | spoke | spoken |
| read | read | read |
| spend | spent | spent |
| cut | cut | cut |
| send | sent | sent |
| build | built | built |
| grow | grew | grown |
| fall | fell | fallen |
| hold | held | held |
| buy | bought | bought |
| drive | drove | driven |
| break | broke | broken |
| learn | learned | learned / learnt |
| forget | forgot | forgotten / forgot |

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
