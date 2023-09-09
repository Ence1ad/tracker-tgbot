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

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV PATH="/opt/venv/bin:$PATH"
WORKDIR usr/src/app
COPY tgbot usr/src/app/tgbot
#CMD ["python", "-m", "tgbot"]