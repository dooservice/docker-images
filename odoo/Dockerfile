ARG ODOO_VERSION=17.0
FROM odoo:${ODOO_VERSION}

USER root

RUN groupadd -g 1500 dooservice \
 && useradd -u 1500 -g 1500 -d /var/lib/odoo -s /bin/bash dooservice \
 && chown -R dooservice:dooservice /var/lib/odoo /mnt/extra-addons /etc/odoo \
 && mkdir -p /mnt/backups \
 && chown dooservice:dooservice /mnt/backups

ARG ODOO_VERSION
COPY cli-patches/ /tmp/cli-patches/
RUN chmod +x /tmp/cli-patches/apply.sh \
 && /tmp/cli-patches/apply.sh ${ODOO_VERSION} \
 && rm -rf /tmp/cli-patches/

COPY entrypoint.sh /dooservice-entrypoint.sh
RUN chmod +x /dooservice-entrypoint.sh

USER dooservice
ENTRYPOINT ["/dooservice-entrypoint.sh"]
CMD ["odoo"]
