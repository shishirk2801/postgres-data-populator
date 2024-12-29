FROM python:3.9-slim

WORKDIR /data-populator

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY populate_data.py .

CMD ["python", "populate_data.py"]
