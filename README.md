# speech_app

This application is a containerized, Python-based speech to text application that converts Youtube videos to transcripts using AI.


1. Clone this repo to your local machine.

2. If you don't already have docker installed. Install it at https://www.docker.com/products/docker-desktop.

3. CD into the speech_app/speech directory.

4. On the command line enter [Docker build --tag=speech .] to build a Docker image of the program. Docker will build an image with all required dependencies to create a container for the speech program.

5. Once Docker has built the image, enter [Docker run speech] on the command line while in the speech_app/speech directory. This will create a container running the speech program. Docker volumes haven't been set up yet, so the program will execute but the transcript will not be stored on your computer.
