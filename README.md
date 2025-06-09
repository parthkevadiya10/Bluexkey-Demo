# Sum Service

A simple Python service that provides sum calculation functionality.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Service

### Using Python
```bash
python -m sum_service
```

### Using Docker
```bash
docker-compose up
```

## API Endpoints

- `POST /sum`: Calculate sum of numbers
  - Request body: `{"numbers": [1, 2, 3]}`
  - Response: `{"result": 6}`

## Development

- Source code is in the `sum_service` directory
- Dependencies are managed in `requirements.txt`
- Docker configuration is in `Dockerfile` and `docker-compose.yml` 