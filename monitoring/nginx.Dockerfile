# Use the official Nginx image as a base image
FROM nginx:1.25.2

# Install Apache2-utils to get the htpasswd command
RUN apt-get update && apt-get install -y apache2-utils && rm -rf /var/lib/apt/lists/*

# Create an .htpasswd file with a sample user (replace with your own)
RUN htpasswd -c /etc/nginx/.htpasswd sample_user

ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME
# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf && mkdir -p /root/certs/example.com

# Generate a self-signed SSL/TLS certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /root/certs/example.com/selfsigned.key -out /root/certs/example.com/selfsigned.crt -subj "/C=US/ST=State/L=City/O=Organization/OU=Organizational Unit/CN=example.com"

COPY container_conf/nginx/nginx_healthcheck.sh $APP_HOME
RUN chmod +x $APP_HOME/nginx_healthcheck.sh

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 CMD $APP_HOME/nginx_healthcheck.sh

