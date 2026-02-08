# SUVIDHA Backend

FastAPI-based REST API for the SUVIDHA digital helpdesk system.

## Development

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Run development server
uvicorn app.main:app --reload --port 8000

# Seed demo data (requires running database)
python seed_data.py
```

## API Documentation

Once running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Structure

```
app/
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic validation
├── routers/        # API endpoints
├── middleware/     # Request processing
├── utils/          # Shared utilities
├── config.py       # Environment configuration
├── database.py     # Database connection
└── main.py         # Application entry
```

## Testing

```bash
pytest --cov=app tests/
```
