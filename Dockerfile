# Use an official Python runtime as a base image
FROM python:3.9-slim

WORKDIR /app

# Copy requirements file first to cache dependencies
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the app
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
