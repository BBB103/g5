# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port (change if your app uses a different port)
EXPOSE 5000

# Set environment variable for Flask (if using Flask)
ENV FLASK_APP=server.py

# Start the app
CMD ["python", "server.py"]