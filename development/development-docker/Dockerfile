FROM debian:jessie

RUN apt-get update && \
    apt-get install -y ircd-hybrid irssi && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN sed -i 's|flags = need_ident;|# flags = need_ident;|g' /etc/ircd-hybrid/ircd.conf
COPY irssi.conf /root/.irssi/config
COPY start.sh /start.sh

ENTRYPOINT ["/start.sh"]
