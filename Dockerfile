FROM alpine:3.4

RUN apk add --no-cache python3 git && \
    pip3 install git+https://github.com/pyfibot/pyfibot3.git && \
    mkdir -p /root/.config/pyfibot

VOLUME /root/.config/pyfibot

ENTRYPOINT ["pyfibot"]
