
# Address Book API

A minimal RESTful API for managing addresses with geospatial search,
built with **FastAPI**, **SQLAlchemy 2.0**, **SQLite**, and **geopy**.

## Features

- Full CRUD for addresses (create, read, update, delete)
- Geospatial query — find addresses within a radius of any coordinate
- Input validation via Pydantic v2
- Request/response logging with configurable severity
- Automatic Swagger UI at `/docs` and ReDoc at `/redoc`
- Docker support
- 20+ integration tests

## Prerequisites

- Python 3.10+
- pip (or Docker)

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/IdanTheMan/address-book-app
cd address-book-api

# 2. Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install production dependencies
pip install -r requirements.txt

# 4. (Optional) Copy the example env file — defaults work out of the box
cp .env.example .env

# 5. Run the server
uvicorn app.main:app --reload
```

The API is now live at **http://localhost:8000**.

| URL | Description |
|---|---|
| http://localhost:8000/docs | Swagger UI (interactive) |
| http://localhost:8000/redoc | ReDoc |

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Docker

Docker lets you run the application in an isolated container without
installing Python or any dependencies on your machine.

### Build the image

```bash
docker build -t address-book-api .
```

This reads the `Dockerfile`, installs Python 3.12 with all dependencies,
and packages the app into an image tagged `address-book-api`.

### Run the container

```bash
docker run -p 8000:8000 address-book-api
```

This starts the container and maps port 8000 inside the container to
port 8000 on your machine. The API is now live at
**http://localhost:8000/docs**.

### Run in the background (detached mode)

```bash
docker run -d -p 8000:8000 --name address-book address-book-api
```

To view logs:

```bash
docker logs address-book
```

To stop and remove the container:

```bash
docker stop address-book
docker rm address-book
```

### Run with environment variables

```bash
docker run -p 8000:8000 -e LOG_LEVEL=DEBUG -e DATABASE_URL=sqlite:///./data/app.db address-book-api
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./addressbook.db` | SQLAlchemy connection string |
| `LOG_LEVEL` | `INFO` | Python log level (`DEBUG`, `INFO`, `WARNING`, ...) |

Create a `.env` file in the project root (see `.env.example`) to override
defaults.

## API Reference

### Create address

```
POST /api/v1/addresses/
```

```json
{
  "street": "1 Infinite Loop",
  "city": "Cupertino",
  "state": "CA",
  "postal_code": "95014",
  "country": "USA",
  "latitude": 37.3318,
  "longitude": -122.0312
}
```

Only `street`, `city`, `country`, `latitude`, and `longitude` are required.

### List addresses

```
GET /api/v1/addresses/?skip=0&limit=100
```

### Get address by ID

```
GET /api/v1/addresses/{id}
```

### Update address (partial)

```
PUT /api/v1/addresses/{id}
```

Send only the fields you want to change. At least one field is required.

```json
{ "street": "2 Infinite Loop" }
```

### Delete address

```
DELETE /api/v1/addresses/{id}
```

### Search nearby

```
GET /api/v1/addresses/nearby?latitude=37.3318&longitude=-122.0312&distance_km=50
```

Returns addresses within the given radius, sorted by distance. Each result
includes a `distance_km` field.

## Project Structure

```
app/
├── main.py           # App factory, middleware, lifespan
├── config.py         # Environment-based settings (pydantic-settings)
├── database.py       # Engine, session, get_db dependency
├── models.py         # SQLAlchemy ORM model (Address)
├── schemas.py        # Pydantic request / response schemas
├── crud.py           # Database operations & geospatial search
└── routers/
    └── addresses.py  # Route handlers
tests/
├── conftest.py       # Fixtures (in-memory DB, TestClient)
└── test_addresses.py # Integration tests
```