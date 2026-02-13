FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the pipeline
CMD ["python", "main.py"]
