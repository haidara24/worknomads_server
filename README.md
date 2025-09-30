# WorkNomads Project

This project consists of a **Django backend server**, an **authentication server** using JWT (RS256), and a **Flutter frontend**. It supports uploading images and audio with secure JWT-based authentication.

---

## Table of Contents

* [Requirements](#requirements)
* [Setup](#setup)

  * [Docker Setup](#docker-setup)
  * [Environment Variables](#environment-variables)
* [Running the Project](#running-the-project)
* [API Endpoints](#api-endpoints)
* [Flutter App](#flutter-app)
* [Troubleshooting](#troubleshooting)

---

## Requirements

* Docker & Docker Compose
* Flutter SDK
* Python 3.13+ (for local dev, optional if using Docker)

---

## Setup

### Docker Setup

1. Clone the project:

```bash
git clone <repo_url>
cd worknomads_task
```

2. Make sure the `keys` folder exists inside the `auth_server` folder:

```
./auth_server/keys/private.pem
./auth_server/keys/public.pem
```

3. Build and run containers:

```bash
docker-compose build --no-cache
docker-compose up -d
```

4. Verify keys are mounted inside the auth server container:

```bash
docker exec -it auth-server ls -l /app/keys
```

You should see:

```
private.pem
public.pem
```

### Environment Variables

**auth_server/.env**

```env
DEBUG=1
DJANGO_SECRET_KEY=<your_secret_key>

# Postgres
POSTGRES_DB=auth_db
POSTGRES_USER=auth_user
POSTGRES_PASSWORD=auth_pass
POSTGRES_HOST=auth_db
POSTGRES_PORT=5432

# RSA keys
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem

# SimpleJWT settings
ACCESS_TOKEN_LIFETIME_MINUTES=15
REFRESH_TOKEN_LIFETIME_DAYS=7
```

**backend_server/.env** (example)

```env
BACKEND_DB_NAME=worknomads
BACKEND_DB_USER=user
BACKEND_DB_PASSWORD=password
BACKEND_DB_HOST=db
BACKEND_DB_PORT=5432
AUTH_SERVER_URL=http://10.0.2.2:8000
```


---

## Running the Project

Start all services:

```bash
docker-compose up -d
```

Check logs:

```bash
docker-compose logs -f auth-server
docker-compose logs -f backend_server
```

Access:

* Auth server: `http://localhost:8000/`
* Backend server: `http://localhost:8001/`

---

## API Endpoints

### Authentication

* **Register:** `POST /auth/register/`
  Body: `{ "username": "user", "password": "pass" }`

* **Token:** `POST /auth/token/`
  Body: `{ "username": "user", "password": "pass" }`

### Uploads

* **Upload Image:** `POST /upload/image/`
  Header: `Authorization: Bearer <access_token>`
  Body: Form-data with `image` file

* **Upload Audio:** `POST /upload/audio/`
  Header: `Authorization: Bearer <access_token>`
  Body: Form-data with `audio` file

* **List Files:** `GET /files/`
  Header: `Authorization: Bearer <access_token>`

---

## Flutter App

The Flutter app connects to:

* `auth_server` (10.0.2.2:8000) for authentication
* `backend_server` (10.0.2.2:8001) for uploads and file management

Ensure `api_client.dart` includes:

```dart
dio.options.headers["Authorization"] = "Bearer \${await SecureStorage.getAccessToken()}";
```

---

## Troubleshooting

* **RS256 Tokens still HS256:**
  Make sure keys are properly mounted and readable:

```bash
docker exec -it auth-server cat /app/keys/private.pem
```

* **Invalid host in auth server:**
  Ensure `ALLOWED_HOSTS` in `auth_server/settings.py` includes:

```python
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
```

* **Flutter cannot reach server:**
  Use `10.0.2.2` for Android emulator to access host machine.

* **Docker caching issues:**
  Rebuild without cache:

```bash
docker-compose build --no-cache
docker-compose up -d
```
