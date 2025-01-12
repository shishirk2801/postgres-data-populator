#!/bin/bash

# Run the data population script
echo "Populating database..."
python populate_data.py

# Start the FastAPI server
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
