#!/bin/sh

# Function to check the health of the Telegram bot API
check_health() {
  # Set your bot token here
    # Access the BOT_TOKEN environment variable
  if [ -z "$BOT_TOKEN" ]; then
    echo "BOT_TOKEN is not set. Please set it in your .env file."
    exit 1
  fi

  # Make a request to the Telegram API getUpdates endpoint
  response=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates")

  # Check if the response contains the "ok" field
  if [ -n "$(echo "$response" | grep '\"ok\":false')" ]; then
    echo "Telegram bot API is not healthy."
    exit 1
  else
    echo "Telegram bot API is healthy."
    exit 0
  fi
}

# Check the health of the Telegram bot API
check_health