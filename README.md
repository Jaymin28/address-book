# Address Book API

A minimal FastAPI application for managing addresses with SQLite persistence and geolocation-based proximity search.

---

## Features

| Feature | Details |
|---|---|
| **CRUD** | Create, Read, Update, Delete addresses |
| **Coordinates** | Latitude + longitude stored and validated per address |
| **Validation** | Pydantic v2 schemas with field-level and model-level validation |
| **Proximity search** | Find all addresses within N km of a coordinate using the Haversine formula |
| **Database** | SQLite via SQLAlchemy ORM |
| **Docs** | Auto-generated Swagger UI at `/docs` |

---

## Project Structure

```
.
├── main.py                         # FastAPI app + routes
├── database/
│   ├── session.py                  # SQLAlchemy engine + session factory
│   └── database.py                 # Backwards-compatible re-export
├── models/
│   ├── address.py                  # ORM model (Address table)
│   ├── schemas.py                  # Pydantic schemas (Create / Update / Response)
│   └── models.py                   # Backwards-compatible re-export
├── sample_addresses_script.py      # Seeds 10 sample Surat addresses via API
├── requirements.txt
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.10 or later
- `pip`

### Clone the repository

```bash
git clone https://github.com/Jaymin28/address-book.git
cd address-book
```


## Setup & Run

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn main:app --reload
```

The server will start at **http://127.0.0.1:8000**

### 4. Open the Swagger docs

Navigate to: **http://127.0.0.1:8000/docs**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/address` | Create a new address |
| `GET` | `/addresses` | List all addresses (paginated) |
| `GET` | `/addresses/nearby` | Find addresses within a radius |
| `GET` | `/address/{id}` | Get address by ID |
| `PUT` | `/address/{id}` | Update address (partial supported) |
| `DELETE` | `/address/{id}` | Delete address |

---

## Validation Rules

- `latitude`: float, range **-90 to 90**
- `longitude`: float, range **-180 to 180**
- `name`, `street`, `city`, `country`: required, non-blank strings
- `state`, `postal_code`: optional
- `PUT` requests require **at least one field** to be provided

---

## Distance Formula

Uses the **Haversine formula** to compute great-circle distance:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
d = 2R × atan2(√a, √(1−a))
```

Where R = 6371 km (Earth's mean radius). Accuracy is sufficient for all practical address-book use cases.

---

## Example Usage

### Create an address

```bash
curl -X POST http://localhost:8000/address \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Surat",
    "country": "India",
    "latitude": 21.230639,
    "longitude": 72.821389,
    "name": "Home",
    "postal_code": "395004",
    "state": "Gujarat",
    "street": "123 Main Street"
  }'
```

### Seeding sample addresses

To quickly populate the database with 10 sample addresses in Surat (some within 10 km of each other, some farther apart), you can use the `sample_addresses_script.py` helper script.

1. **Ensure the API server is running:**

   ```bash
   uvicorn main:app --reload
   ```

2. **Run the script:**

   ```bash
   python sample_addresses_script.py
   # or, with the venv:
   # .venv/bin/python sample_addresses_script.py
   ```

The script will call `POST /address` for each sample entry and print the created IDs. You can then explore them via `/addresses`, `/addresses/nearby`, or directly in the Swagger UI at `/docs`.

### Find addresses within 5–10 km of a point

Results are sorted by distance (nearest first) and include a `distance_km` field.

- **Examples according to addresses in the sample script**  

  ```bash
  # within 5 km
  curl "http://localhost:8000/addresses/nearby?latitude=21.1760&longitude=72.8015&distance_km=5"

  curl "http://localhost:8000/addresses/nearby?latitude=21.1535&longitude=72.7860&distance_km=5"

  curl "http://localhost:8000/addresses/nearby?latitude=21.2245&longitude=72.8305&distance_km=5"

  # within 10 km
  curl "http://localhost:8000/addresses/nearby?latitude=21.1760&longitude=72.8015&distance_km=10"

  curl "http://localhost:8000/addresses/nearby?latitude=21.1535&longitude=72.7860&distance_km=10"

  curl "http://localhost:8000/addresses/nearby?latitude=21.2245&longitude=72.8305&distance_km=10"
  ```

---
