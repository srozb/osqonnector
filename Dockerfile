FROM python:2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client mysql-client python-dev libev-dev\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /usr/src/app/osqonnector
EXPOSE 8000
CMD ["./serve_bjoern.sh"]
