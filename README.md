# FastIDV

FastIDV is an async FastAPI service for identity verification workflows.
It combines:

- User authentication with JWT
- NID image upload + OCR extraction through DeepseekOCR
- Face verification + spoof detection through DeepFace [(Using DeepFaceAPI)](https://github.com/rozari0/DeepfaceAPI)
- A gated sample resource ("biscuits") available only to NID verified users

## Tech Stack

- Python
- FastAPI
- Async SQLAlchemy + Alembic
- Tested with PgSQL, Should work with any SQL Databases
- Ollama for hosting DeepSeekOCR and structured extraction
- Deepface for face verification

## Project Structure

```text
app/
	api/routes/      # Route modules: users, idv, biscuits
	core/            # Settings and dependencies
	db/              # Engine/session/base definitions
	models/          # SQLAlchemy models
	schemas/         # Pydantic schemas
	services/        # LLM and deepface client wrappers
	utils/           # JWT and password helpers
alembic/           # Database migrations
uploads/           # Uploaded NID/face images
```

## Prerequisites

Install and run the following before testing full IDV flows:

1. Python 3.14 or newer
2. uv (recommended) for running commands
3. Ollama server at http://localhost:11434 with models:
	 - deepseek-ocr:latest
	 - qwen2.5:latest
4. (DeepFaceAPI)[https://github.com/rozari0/DeepfaceAPI] at http://localhost:8008 exposing:
	 - POST /verify/
	 - POST /analyze/

If external services are not running, authentication and basic endpoints still work, but OCR/verification endpoints will fail.

## Installation

```bash
uv sync
```

## Environment Configuration

Create a .env file in the project root. These are the available settings and defaults:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
SECRET_KEY=CHANGETHISSECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
OLLAMA_API_URL=http://localhost:11434
ECHO_SQLALCHEMY=False
```

For production-like usage, change SECRET_KEY and DATABASE_URL.

## Database Migrations

Apply migrations:

```bash
just migrate
```

Create a new migration:

```bash
just makemigrations 006 your migration message
```

## Run the API

```bash
just
```

This starts:

```text
uv run uvicorn app.main:app --reload
```

Default docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Overview

Base prefix for most endpoints: /api/v1

Public endpoint:

- GET /health

User routes:

- POST /api/v1/users/signup
- POST /api/v1/users/login
- GET /api/v1/users/me

IDV routes (authenticated):

- POST /api/v1/idv/nid
- PUT /api/v1/idv/nid
- GET /api/v1/idv/nid
- POST /api/v1/idv/verify

Biscuits route (authenticated):

- GET /api/v1/biscuits/

## Authentication Flow

1. Sign up with email/password.
2. Log in with OAuth2 form fields (username is your email).
3. Use returned access_token as Bearer token for protected routes.

Example:

```http
Authorization: Bearer <access_token>
```

## Request Examples

### Signup

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/signup" \
	-H "Content-Type: application/json" \
	-d '{"email":"user@example.com","password":"secret123"}'
```

### Login (OAuth2 form)

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/login" \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d "username=user@example.com&password=secret123"
```

### Upload NID

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/idv/nid" \
	-H "Authorization: Bearer <access_token>" \
	-F "file=@/path/to/nid.jpg"
```

### Edit NID Data

```bash
curl -X PUT "http://127.0.0.1:8000/api/v1/idv/nid" \
	-H "Authorization: Bearer <access_token>" \
	-H "Content-Type: application/json" \
	-d '{"name":"Updated Name","dob":"1990-01-01"}'
```

### Verify Face

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/idv/verify" \
	-H "Authorization: Bearer <access_token>" \
	-F "file=@/path/to/selfie.jpg"
```

### Access Biscuits

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/biscuits/" \
	-H "Authorization: Bearer <access_token>"
```

## Helpful Commands

```bash
just format   # import sorting + formatting
just clean    # remove __pycache__ and .pyc files
```

## Notes

- Uploaded files are stored under uploads/<user_id>/.
- The IDV flow marks a user as verified only when both checks pass:
	- Face match is true
	- Spoof check is false
- CORS is currently open to all origins.
- Most of the code is writen by human, except for this README.md File