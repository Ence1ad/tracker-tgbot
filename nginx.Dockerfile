# Use the official Nginx image as a base image
FROM nginx:latest

# Install Apache2-utils to get the htpasswd command
RUN apt-get update && apt-get install -y apache2-utils

# Create an .htpasswd file with a sample user (replace with your own)
RUN htpasswd -c /etc/nginx/.htpasswd sample_user

ENV APP_HOME /usr/src/app
WORKDIR $APP_HOME
# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

COPY container_conf/nginx/nginx_healthcheck.sh $APP_HOME
RUN chmod +x $APP_HOME/nginx_healthcheck.sh

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 CMD $APP_HOME/nginx_healthcheck.sh

