FROM ubuntu:latest

RUN apt update -y && apt upgrade -y
RUN apt install nginx supervisor letsencrypt prometheus-node-exporter python3 -y

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

##
# Configure nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/mirrorhub-client /etc/nginx/sites-available/mirrorhub-client
RUN rm /etc/nginx/sites-enabled/default

##
# Configure Letsencrypt
RUN mkdir -p /tmp/letsencrypt

RUN mkdir -p /srv/internals

COPY init_mirrorhub_client /usr/local/bin/
CMD init_mirrorhub_client
