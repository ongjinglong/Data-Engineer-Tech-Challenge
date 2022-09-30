FROM postgres:latest

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD password
ENV POSTGRES_DB carSales

COPY createSchema.sql /docker-entrypoint-initdb.d/
COPY dataIngest.sql /docker-entrypoint-initdb.d/

RUN mkdir /logs
CMD ["postgres", "-c", "log_statement=all", "-c", "log_destination=stderr"]