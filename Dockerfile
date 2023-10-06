# Create builder image
FROM python:3.11-slim-bullseye as builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Create a non-root user
RUN groupadd -r mygroup && useradd -r -g mygroup myuser

# Set the working directory
WORKDIR /usr/src/app

# Copy the virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
COPY tgbot .



# Copy and make the entrypoint script executable
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Specify the non-root user for running the application
USER myuser

# Metadata as labels (optional but useful)
LABEL maintainer="Your Name <fantminer@gmail.com>"
LABEL version="0.0.3"

# Add /opt/venv/bin to PATH (optional)
ENV PATH="/opt/venv/bin:$PATH"

# Define the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]