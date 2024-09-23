# Use the official Python Alpine image from the Docker Hub
FROM python:3.12.3-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

COPY .env .env
# Expose the port the app runs on
EXPOSE 5050

# Set the entrypoint and ensure the script is executable
ENTRYPOINT ["sh", "-c", "chmod +x /app/scripts/start.sh && /app/scripts/start.sh"]
