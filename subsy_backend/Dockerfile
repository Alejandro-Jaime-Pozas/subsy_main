# name of the tag; py version 3.10, alpine is a linux based lightweight version of python
FROM python:3.10-alpine3.19
LABEL maintainer="https://portfolio-alejandro-jaime.web.app/"

# sets python unbuffered to true so that python logs are directly displayed when container is running
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    # apk lines reference python-postgres adaptor dependencies req for this alpine image so that postgres can work in this image
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    # this below deletes all virtual deps from above within same command ie build-base, etc
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"
ENV PYTHONPATH="/app"

USER django-user
