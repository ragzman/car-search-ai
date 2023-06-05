# Use the Python 3 base image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Node.js
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install Angular CLI
RUN npm install -g @angular/cli

# Copy the application code to the container
COPY . .

# Install Node.js dependencies
RUN npm install

# Install Gulp globally
RUN npm install -g gulp

# Build the frontend assets
RUN gulp

# Build the frontend
RUN cd frontend && npm install && ng build

# Expose the port used by the application (if needed)
EXPOSE 8000

# Start the backend server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
