# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the FLASK_APP environment variable to point to financial.py
ENV FLASK_APP=financial.py

# Run the application, binding to all interfaces
CMD ["flask", "run", "--host=0.0.0.0"]
