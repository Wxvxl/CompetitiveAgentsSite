# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all other files
COPY . .

# Expose port
EXPOSE 5000

# Run database initialization and start Flask
CMD ["sh", "-c", "python db/init_db.py && flask run --host=0.0.0.0"]
