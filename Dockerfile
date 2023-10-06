# create builder image
FROM python:3.11-slim-bullseye as builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Final image
FROM python:3.11-slim-bullseye
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

LABEL maintainer="Your Name <fantminer@gmail.com>"
LABEL version="0.0.3"

# Create a non-root user
RUN groupadd -r mygroup && useradd -r -g mygroup myuser

WORKDIR usr/src/app
COPY entrypoint.sh usr/src/app/

COPY . .

# Copy and make the entrypoint script executable
#COPY ./entrypoint.sh usr/src/app/entrypoint.sh
#COPY entrypoint.sh usr/src/app/
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# Switch to the myuser user
USER myuser
# Define the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]