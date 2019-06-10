# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Set the working directory to /speech
WORKDIR /speech

# Copy the current directory contents into the container at /speech
COPY . /speech

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run speech.py when the container launches
CMD ["python", "speech.py"]