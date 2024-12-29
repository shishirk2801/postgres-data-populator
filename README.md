# Postgres Data Populator with Docker

This project provides a Dockerized environment to populate a PostgreSQL database with 1 million rows of fake data using Python and Faker. The project uses Docker Compose to manage the database and Python services.

## Setup Instructions

### Step 1: Clone the Repository

Start by cloning the repository to your local machine:
```bash
git clone https://github.com/utksngh/postgres-data-populator.git
cd postgres-data-populator
```
### Step 2: Build the Docker Containers

```bash
docker-compose up
```
### Step 3: Start the Containers

```bash
docker-compose up
```
### Accessing the Database

```bash
docker exec -it postgres_db psql -U user -d test_db
```
```bash
SELECT COUNT(*) FROM test_table;
```

