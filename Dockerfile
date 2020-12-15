# Install the base requirements for the app.
# This stage is to support development.
# FROM python:alpine AS base
FROM python:3
WORKDIR /app
COPY lights.py .
CMD python ./lights.py