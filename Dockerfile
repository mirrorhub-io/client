FROM ubuntu:latest

RUN apt update -y && apt upgrade -y
RUN apt install nginx -y

CMD echo "works"
