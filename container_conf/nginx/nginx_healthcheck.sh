#!/bin/sh

# Function to check the health of a given URL
check_health() {
  url="$1"

  # Make a request to the provided URL
  response=$(curl -s "$url")

  # Check if the response contains the "OK" field
  if [ -n "$(echo "$response" | grep 'OK')" ]; then
    echo "Service is healthy."
    exit 0
  else
    echo "Service is not healthy."
    exit 1
  fi
}

# Check the health of the Nginx server
check_health "http://localhost/health"