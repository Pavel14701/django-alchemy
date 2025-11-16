# Django‑Alchemy

**Django‑Alchemy** is a framework project that combines **Django** and **SQLAlchemy**, with migrations powered by **Alembic**, dependency injection via **Dishka**, and modern serialization libraries (**Adaptix**, **Msgspec**).  
The architecture follows *Clean Architecture* principles, with clear separation into `application`, `domain`, and `infrastructure` layers, plus dedicated modules for `products` and `users`.

---

## 🚀 Features

- Django as the entry point (ASGI/WSGI, middleware, urls, settings).
- SQLAlchemy instead of the default Django ORM.
- Alembic migrations (`migrations/versions`).
- Redis for session storage.
- Dependency injection container via Dishka (`container.py`, `ioc.py`).
- Layered structure:
  - **application** — services, interactors, interfaces  
  - **domain** — entities and business rules  
  - **infrastructure** — database, repositories, middleware  
  - **controllers** — schemas and views  

---

## 📦 Installation & Run

### 1. Clone the repository

```bash
git clone https://github.com/Pavel14701/django-alchemy.git
cd django-alchemy
```

### 2. Install dependencies

This project uses Python 3.12+ and [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

### 3. Run the server

```bash
uv run python manage.py runserver
```

---

## 🔧 Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "add products table"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

---

## 🗂️ Project Structure

```text
├── main/              # core app (settings, urls, middleware)
│   ├── application/   # services, interfaces
│   ├── domain/        # entities
│   └── infrastructure # db, redis, sessions
│
├── products/          # product catalog module
│   ├── application/   # DTOs, interactors, services
│   ├── controllers/   # schemas, views
│   ├── domain/        # entities
│   └── infrastructure # models, repositories
│
├── users/             # user management module
│   ├── application/   # interactors, services, errors
│   ├── controllers/   # schemas, views
│   ├── domain/        # entities
│   └── infrastructure # models, repositories, security
│
├── migrations/        # alembic migrations
├── alembic.ini        # alembic config
├── container.py       # DI container
├── ioc.py             # dependency wiring
└── manage.py          # Django entry point
```

---

## 🧪 Development Tools

- **ruff** — linting & formatting (configured in `pyproject.toml`).  
- **mypy** — static type checking.  

Run checks:

```bash
uv run ruff check .
uv run mypy .
```

---

## 📖 Example API

Once the server is running, endpoints are available at:

```
http://localhost:8000
```

Examples:

- `GET /products/` — list products  
- `POST /users/login/` — user login  
- `POST /users/register/` — user registration  

---

## 🤝 Contributing

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature/foo`).  
3. Commit your changes.  
4. Open a Pull Request.  

---

## 📜 License

MIT License.
