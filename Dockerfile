# Builder image
FROM python:3.11-slim-bullseye as builder

# Set up virtual environment
RUN python -m venv /opt/venv
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11-slim-bullseye

# Copy the virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Environment variables
ENV APP_HOME /usr/src/app
ENV PATH="/opt/venv/bin:$PATH"

# Metadata labels
LABEL maintainer="<fantminer@gmail.com>"
LABEL version="alpha 0.0.1"

# Create a non-root user and set working directory
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
WORKDIR $APP_HOME

# Copy the entrypoint script
COPY entrypoint.sh $APP_HOME
# Copy application code
COPY . .

# Set permissions for entrypoint and healthcheck scripts
RUN chmod +x $APP_HOME/entrypoint.sh

# Switch to the myuser user
USER appuser

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]