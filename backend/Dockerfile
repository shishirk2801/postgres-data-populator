FROM golang:1.21-alpine AS builder

WORKDIR /build
COPY main.go .
COPY go.mod go.sum ./
RUN go build -o excel-generator .

FROM python:3.11-slim

WORKDIR /app

# Install build dependencies and golang
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Go binary from builder
COPY --from=builder /build/excel-generator /app/excel-generator

# Copy Python code
COPY *.py .

# Make the Go binary executable
RUN chmod +x /app/excel-generator

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

# Use entrypoint script instead of direct CMD
ENTRYPOINT ["/app/entrypoint.sh"]
