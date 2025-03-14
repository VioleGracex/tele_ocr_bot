# Use an official Python runtime as a parent image
FROM python:3.13.2

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the bot
CMD ["python", "bot/main.py"]