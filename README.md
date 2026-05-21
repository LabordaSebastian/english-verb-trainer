# 🎯 English Irregular Verb Trainer — DevOps Edition

> Aplicación híbrida (CLI + Web UI) para practicar verbos irregulares en inglés, construida con un stack de herramientas reales de DevOps: Python, PostgreSQL, Docker y GitHub Actions.

[![Docs](https://img.shields.io/badge/Docs-MkDocs-blue?logo=markdown)](https://labordasebastian.github.io/english-verb-trainer/)
[![CI](https://github.com/LabordaSebastian/english-verb-trainer/actions/workflows/ci.yml/badge.svg)](https://github.com/LabordaSebastian/english-verb-trainer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 ¿Qué hace esta aplicación?

El programa cuenta con una interfaz web moderna y también funciona en modo consola. Te pregunta un verbo en inglés en su forma base (por ejemplo **READ**) y vos tenés que responder con el **pasado simple** y el **participio pasado**, separados por un espacio.

### ✨ Web UI (Dark Mode)

<p align="center">
  <img src="assets/home.png" width="45%" alt="Home Screen">
  <img src="assets/quiz.png" width="45%" alt="Quiz Screen">
</p>
<p align="center">
  <img src="assets/results.png" width="45%" alt="Results Screen">
  <img src="assets/stats.png" width="45%" alt="Stats Screen">
</p>

### 💻 CLI (Terminal)


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

## 📚 Documentación completa

Para una guía detallada sobre arquitectura, desarrollo y deployment, consulta la **[documentación oficial](https://labordasebastian.github.io/english-verb-trainer/)**.

En la documentación encontrarás:
- **Quick Start** — Cómo levantar el proyecto en 5 minutos
- **Guías técnicas** — Arquitectura, flujo de datos, modelos de BD
- **Referencia API** — Endpoints, esquemas, ejemplos
- **CLI Reference** — Todos los comandos disponibles
- **Guía de desarrollo** — Setup local, testing, contribuciones

[→ Acceder a la documentación](https://labordasebastian.github.io/english-verb-trainer/)

---

## ⚡ Quick Start — Un solo comando

> Solo necesitás **Docker Desktop** instalado. Nada más.

```bash
git clone https://github.com/LabordaSebastian/english-verb-trainer.git
cd english-verb-trainer

# Crear archivo de variables de entorno
cp .env.example .env

# Iniciar la aplicación
docker compose -f docker/docker-compose.yml up
```

Abrí **http://localhost:8000** en tu browser y listo. 🎯

Docker Compose levanta automáticamente:
- 🐘 PostgreSQL 15 (con datos persistentes)
- 🌱 Carga los 100 verbos irregulares + 1000 palabras de vocabulario
- 🚀 Web app en **http://localhost:8000**

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
- `verb-trainer quiz` — inicia el quiz
- `verb-trainer seed` — carga los verbos en la base de datos (requiere PostgreSQL)
- `verb-trainer stats` — muestra el progreso del usuario

**¿Por qué Typer?**
- Genera automáticamente el `--help` de cada comando.
- Permite agregar opciones como `--verb read` o `--rounds 20` de forma simple.
- Es el estándar moderno para CLIs en Python.

```bash
# Ejemplos de uso con opciones
verb-trainer quiz --verb go        # practica solo el verbo GO
verb-trainer quiz --rounds 20      # quiz de 20 preguntas
verb-trainer stats                 # ver tu progreso
```

---

### 🐘 PostgreSQL 15

**¿Qué es?**
[PostgreSQL](https://www.postgresql.org/) es uno de los motores de base de datos relacionales más populares y robustos del mundo. Es ampliamente utilizado en producción por empresas de todo tamaño.

**¿Para qué se usa acá?**
Almacena cuatro tablas:

| Tabla | Contenido |
|---|---|
| `verbs` | Los 100 verbos irregulares (base, pasado, participio, formas alternativas) |
| `user_attempts` | Cada intento del usuario: qué respondió, si fue correcto, y cuándo |
| `vocabulary_words` | Las 1000 palabras más comunes del inglés con traducción y categoría |
| `vocab_attempts` | Cada intento del quiz de vocabulario |

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



### 🐳 Docker

**¿Qué es?**
[Docker](https://www.docker.com/) es la plataforma de contenedores más utilizada en DevOps. Permite empaquetar aplicaciones con todas sus dependencias en una imagen portable que corre igual en cualquier máquina.

**¿Para qué se usa acá?**
1. **PostgreSQL + Web App**: Usamos Docker Compose para orquestar la base de datos oficial `postgres:15` junto con nuestra aplicación web. Así no tenés que instalar PostgreSQL ni Python en tu máquina.

2. **Imagen de la app**: El `Dockerfile` empaqueta la aplicación (FastAPI y SPA) para que cualquiera pueda correrla:
   ```bash
   docker run -p 8000:8000 -e DATABASE_URL=... ghcr.io/labordaSebastian/english-verb-trainer:latest
   ```

<p align="center">
  <img src="assets/Diagrama_infraestructura.png" width="420" alt="Diagrama de infraestructura Docker Compose">
</p>

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
├── app/                        # Lógica core y CLI
│   ├── cli.py                  # Entry point CLI (verb-trainer)
│   ├── database.py             # Conexión SQLAlchemy a PostgreSQL
│   ├── models.py               # Tablas: Verb, UserAttempt, VocabularyWord, VocabAttempt
│   ├── quiz.py                 # Lógica: validación, estadísticas
│   ├── seed.py                 # 100 verbos irregulares precargados
│   └── vocab_seed.py           # 1000 palabras de vocabulario precargadas
│
├── docker/                     # Configuración Docker
│   ├── Dockerfile              # Imagen Docker de la aplicación
│   ├── docker-compose.yml      # Orquestador (App + PostgreSQL)
│   └── entrypoint.sh           # Script de inicio del contenedor
│
├── api/                        # Backend REST (FastAPI)
│   ├── main.py                 # Endpoints y servidor web
│   └── schemas.py              # Modelos Pydantic
│
├── static/                     # Frontend SPA (Single Page App)
│   └── index.html              # Interfaz web (Dark mode, JS)
│
├── tests/                      # Tests unitarios
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_quiz.py
│   └── test_seed.py
│
├── docker-compose.yml          # Orquestador (App + PostgreSQL)
├── Makefile                    # Comandos DevOps (make up, make stop, make test)
├── pyproject.toml              # Configuración del proyecto Python
├── .env.example                # Variables de entorno de ejemplo
├── .gitignore                  # Archivos excluidos de Git
│
└── .github/
    └── workflows/
        ├── ci.yml              # CI: lint + pytest en cada push
        ├── cd.yml              # CD: Docker image + Release en cada tag
        └── docs.yml            # Deploy documentación a GitHub Pages
```

---

## 🚀 Cómo usar el proyecto

### Prerequisitos

| Herramienta | Instalación |
|---|---|
| **Python 3.10+** | [python.org](https://www.python.org/downloads/) |
| **Docker Desktop** | [docker.com](https://www.docker.com/products/docker-desktop/) |



### Comandos disponibles

```bash
# Iniciar quiz aleatorio (10 preguntas)
verb-trainer quiz

# Practicar un verbo específico
verb-trainer quiz --verb read

# Quiz más largo
verb-trainer quiz --rounds 20

# Ver tu progreso y verbos más difíciles
verb-trainer stats

# Recargar los verbos en la DB
verb-trainer seed

# Cargar las 1000 palabras de vocabulario
verb-trainer vocab-seed
```

### Comandos con Makefile (Linux/Mac)

```bash
make up        # inicia Postgres y la Web App (Docker Compose)
make stop      # detiene contenedores (mantiene datos)
make destroy   # detiene y elimina todo (incluye datos)
make test      # corre los tests
make lint      # verifica el estilo del código
make quiz      # corre el modo terminal (requiere python local)
make clean     # elimina el entorno virtual y caché
make help      # muestra todos los comandos disponibles
```

### Puertos

| Servicio | URL |
|---|---|
| **Web App** | http://localhost:8000 |
| **PostgreSQL** | localhost:5432 |

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
```bash
# Creás un docker-compose.yml con postgres y la app apuntando a la imagen de GHCR:
docker run -p 8000:8000 \
  --env DATABASE_URL=postgresql://user:pass@host:5432/db \
  ghcr.io/labordaSebastian/english-verb-trainer:latest
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

## 📚 Los 100 Verbos Irregulares

### Verbos 1–50

| Base | Pasado | Participio |
|---|---|---|
| be | was/were | been |
| have | had | had |
| do | did | done |
| go | went | gone |
| say | said | said |
| get | got | gotten |
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

### Verbos 51–100

| Base | Pasado | Participio |
|---|---|---|
| catch | caught | caught |
| fight | fought | fought |
| teach | taught | taught |
| sell | sold | sold |
| choose | chose | chosen |
| sleep | slept | slept |
| win | won | won |
| hang | hung | hung |
| draw | drew | drawn |
| fly | flew | flown |
| wear | wore | worn |
| throw | threw | thrown |
| steal | stole | stolen |
| hide | hid | hidden |
| shake | shook | shaken |
| wake | woke | woken |
| rise | rose | risen |
| bite | bit | bitten |
| swim | swam | swum |
| sing | sang | sung |
| ring | rang | rung |
| drink | drank | drunk |
| eat | ate | eaten |
| feed | fed | fed |
| lend | lent | lent |
| bend | bent | bent |
| burn | burned | burned / burnt |
| dream | dreamed | dreamed / dreamt |
| kneel | knelt | knelt |
| sweep | swept | swept |
| weep | wept | wept |
| creep | crept | crept |
| leap | leaped | leaped / leapt |
| deal | dealt | dealt |
| knit | knit | knit / knitted |
| hit | hit | hit |
| hurt | hurt | hurt |
| cost | cost | cost |
| spread | spread | spread |
| shed | shed | shed |
| split | split | split |
| beat | beat | beaten |
| forbid | forbade | forbidden |
| forgive | forgave | forgiven |
| undertake | undertook | undertaken |
| overcome | overcame | overcome |
| withdraw | withdrew | withdrawn |
| mistake | mistook | mistaken |
| arise | arose | arisen |
| bind | bound | bound |

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
