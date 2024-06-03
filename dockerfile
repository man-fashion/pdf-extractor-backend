## to build image - 
## docker build -t flask-app .
##
## to run image
## docker run -p 5050:5050 flask-app
##

# Use the official Python Alpine image from the Docker Hub
FROM python:3.12.3-slim

# Install only the necessary tools
#RUN apt-get update && apt-get install -y gcc 

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5050

# Grant execute permissions to the entrypoint script
RUN chmod +x /app/scripts/start.sh

# Set the entrypoint
ENTRYPOINT ["/app/scripts/start.sh"]

