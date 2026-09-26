#!/bin/sh
set -eu

certificate_dir="/etc/letsencrypt/live/${DOMAIN}"
if [ -s "${certificate_dir}/fullchain.pem" ] && [ -s "${certificate_dir}/privkey.pem" ]; then
    cp /etc/nginx/templates/http-redirect.conf /etc/nginx/conf.d/default.conf
    envsubst '${DOMAIN}' < /etc/nginx/templates/https.conf > /etc/nginx/conf.d/https.conf
else
    cp /etc/nginx/templates/http-bootstrap.conf /etc/nginx/conf.d/default.conf
    rm -f /etc/nginx/conf.d/https.conf
fi

(while :; do sleep 12h; nginx -s reload; done) &
exec nginx -g 'daemon off;'