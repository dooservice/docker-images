ARG ODOO_VERSION=17.0
ARG ODOO_BASE=odoo:${ODOO_VERSION}
FROM ${ODOO_BASE}

USER root

RUN groupadd -g 1500 dooservice \
 && useradd -u 1500 -g 1500 -d /var/lib/odoo -s /bin/bash dooservice \
 && mkdir -p /mnt/addons /mnt/backups \
 && chown -R dooservice:dooservice /var/lib/odoo /mnt/extra-addons /mnt/addons /etc/odoo \
 && chown dooservice:dooservice /mnt/backups

ARG ODOO_VERSION
COPY cli-patches/ /tmp/cli-patches/
RUN chmod +x /tmp/cli-patches/apply.sh \
 && /tmp/cli-patches/apply.sh ${ODOO_VERSION} \
 && rm -rf /tmp/cli-patches/

# The Dooservice module (tickets to the consultancy) and Connect, at the commit
# odoo/addons.toml names for this version, on every environment's addons path: the module
# installed only when somebody installs it from Apps, Connect loaded as a server-wide module
# from odoo.conf and never installed.
ARG ADDONS_COMMIT
LABEL sh.dooservice.addons-commit="${ADDONS_COMMIT}"
RUN test -n "${ADDONS_COMMIT}" \
 && mkdir -p /tmp/dooservice-addons /opt/dooservice/addons \
 && curl -fsSL "https://codeload.github.com/dooservice/odoo-addons/tar.gz/${ADDONS_COMMIT}" \
      | tar -xz --strip-components=1 -C /tmp/dooservice-addons \
 && test -f /tmp/dooservice-addons/dooservice_brain/__manifest__.py \
 && test -f /tmp/dooservice-addons/dooservice_connect/__manifest__.py \
 && mv /tmp/dooservice-addons/dooservice_brain /opt/dooservice/addons/dooservice_brain \
 && mv /tmp/dooservice-addons/dooservice_connect /opt/dooservice/addons/dooservice_connect \
 && rm -rf /tmp/dooservice-addons \
 && chmod -R a+rX,go-w /opt/dooservice

COPY entrypoint.sh /dooservice-entrypoint.sh
RUN chmod +x /dooservice-entrypoint.sh

USER dooservice
ENTRYPOINT ["/dooservice-entrypoint.sh"]
CMD ["odoo"]
