#!/bin/bash

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Environment file not found. Creating from example..."
    cp .env.example .env
    echo "Please edit .env to add your OpenAI API key"
    exit 1
fi

# Source environment variables
export $(cat .env | xargs)

# Run the server
echo "Starting Life Insurance Support Assistant..."
echo "Visit http://localhost:8000/docs for API documentation"
uvicorn app.main:app --host $APP_HOST --port $APP_PORT --reload