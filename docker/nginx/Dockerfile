FROM nginx:1.28-alpine

COPY http-bootstrap.conf http-redirect.conf https.conf /etc/nginx/templates/
COPY entrypoint.sh /usr/local/bin/stockpro-nginx-entrypoint
RUN chmod 0555 /usr/local/bin/stockpro-nginx-entrypoint

ENTRYPOINT ["/usr/local/bin/stockpro-nginx-entrypoint"]