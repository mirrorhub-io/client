FROM ubuntu:latest

RUN apt update -y && apt upgrade -y
RUN apt install nginx supervisor letsencrypt prometheus-node-exporter python3 python3-jinja2 -y

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

##
# Configure nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

RUN mkdir -p /srv/internals
COPY internals/mirror.j2 /srv/internals/mirror.j2
COPY internals/mirror_nonssl.j2 /srv/internals/mirror_nonssl.j2

RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/sites-available/default

##
# Configure Letsencrypt
RUN mkdir -p /tmp/letsencrypt

RUN mkdir -p /srv/nginx

COPY init_mirrorhub_client.py /usr/local/bin/
CMD init_mirrorhub_client.py
