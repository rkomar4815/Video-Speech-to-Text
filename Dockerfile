# Use an official Python runtime as a parent image
FROM python:3.7-slim

# Make code directory

RUN mkdir /code

# Set the working directory to /code
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY requirements.txt /code/

# Install any needed packages specified in requirements.txt
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y --no-install-recommends gcc
RUN apt-get install -y ffmpeg
RUN apt-get install -y python3-dev
RUN apt-get install -y libpq-dev
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /code/



 