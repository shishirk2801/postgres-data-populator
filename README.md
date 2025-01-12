# Postgres Data Populator with Excel Export

A hybrid Go-Python application that populates PostgreSQL with test data and provides Excel export functionality via FastAPI.

## Architecture

- **FastAPI Backend**: REST API endpoints for triggering data operations
- **Go Binary**: High-performance Excel generation and S3 upload
- **PostgreSQL**: Database for storing test data
- **LocalStack**: Local S3-compatible storage
- **Docker**: Containerization for all components

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/utksngh/postgres-data-populator.git
cd postgres-data-populator
```

2. Start the services:
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Initialize LocalStack (S3)
- Build and run the FastAPI service
- Populate the database with test data
- Start the API server

## API Endpoints

### Generate and Download Excel
```bash
GET /download-xlsx/
```
Generates an Excel file from PostgreSQL data and returns a presigned S3 URL.

## Components

### Database
- PostgreSQL 15
- Contains 1 million rows of test data
- Auto-populated on startup

### FastAPI Backend
- REST API endpoints
- Executes Go binary for Excel operations
- Handles S3 presigned URLs

### Go Excel Generator
- High-performance Excel file generation
- Concurrent data processing
- Direct S3 upload capability

### LocalStack
- S3-compatible local storage
- Available at `http://localhost:4566`

## Development

### Database Access
```bash
docker exec -it postgres_db psql -U user -d test_db
```

### Useful Commands
```bash
# Check database row count
SELECT COUNT(*) FROM test_table;

# Check S3 buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# View logs
docker-compose logs -f backend
```

## Environment Variables

### Database
- `DB_HOST`: Database hostname
- `DB_PORT`: Database port (default: 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

### AWS/LocalStack
- `AWS_ENDPOINT_URL`: LocalStack endpoint
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key

## Project Structure
```
.
├── backend/
│   ├── main.go           # Go Excel generator
│   ├── populate_data.py  # Database population script
│   ├── main.py          # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   ├── Dockerfile       # Multi-stage build
│   └── entrypoint.sh    # Startup script
├── docker-compose.yml
├── init.sql
└── README.md
```

## Performance

- Concurrent Excel generation
- Batch processing of database rows
- Streaming Excel writer to minimize memory usage
- Optimized database queries

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request