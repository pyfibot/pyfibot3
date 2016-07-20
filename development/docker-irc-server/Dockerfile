FROM alpine:3.4

RUN apk --no-cache add ngircd

RUN sed -i 's|;PAM = yes|PAM = no|g' /etc/ngircd/ngircd.conf

ENTRYPOINT ["ngircd", "-n"]
