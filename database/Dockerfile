FROM mcr.microsoft.com/mssql/server:2022-latest

ENV ACCEPT_EULA=Y

COPY ./initialization.sql .

RUN mkdir -p /var/opt/mssql/backup

EXPOSE 1433

CMD [ "/opt/mssql/bin/sqlservr" ]