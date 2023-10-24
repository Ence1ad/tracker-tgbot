#!/bin/sh

# Check if migrations need to be applied
alembic upgrade head

# Start your application
python -m tgbot