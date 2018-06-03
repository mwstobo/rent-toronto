FROM alpine:3.6

COPY *.py requirements.txt /opt/apartment/
WORKDIR /opt/apartment

RUN apk update \
 && apk add --no-cache \
            --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ \
            python3 \
            ca-certificates \
            geos \
            musl-dev \
 && update-ca-certificates \
 && python3 -m ensurepip \
 && rm -r /usr/lib/python*/ensurepip \
 && pip3 install -r requirements.txt

VOLUME ["/opt/apartment/kml"]

CMD ["python3.6", "main.py"]
