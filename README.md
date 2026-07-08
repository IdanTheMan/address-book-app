
# Address Book API

A minimal RESTful API for managing addresses with geospatial search,
built with **FastAPI**, **SQLAlchemy 2.0**, **SQLite**, and **geopy**.

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

### Build the image

```bash
docker build -t address-book-api .
```

### Run the container

```bash
docker run -p 8000:8000 address-book-api
```

### Run in the background (detached mode)

```bash
docker run -d -p 8000:8000 --name address-book address-book-api
```