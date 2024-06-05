FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE=CommunicationLTD
COPY ./initialization.sql /docker-entrypoint-initdb.d/
EXPOSE 3306