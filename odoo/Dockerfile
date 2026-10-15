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

# The Dooservice assistant, at the commit odoo/brain.toml names for this version: on every
# environment's addons path, installed only when somebody installs it from Apps.
ARG BRAIN_COMMIT
LABEL sh.dooservice.brain-commit="${BRAIN_COMMIT}"
RUN test -n "${BRAIN_COMMIT}" \
 && mkdir -p /tmp/brain /opt/dooservice/addons \
 && curl -fsSL "https://codeload.github.com/dooservice/odoo-brain/tar.gz/${BRAIN_COMMIT}" \
      | tar -xz --strip-components=1 -C /tmp/brain \
 && test -f /tmp/brain/dooservice_brain/__manifest__.py \
 && mv /tmp/brain/dooservice_brain /opt/dooservice/addons/dooservice_brain \
 && rm -rf /tmp/brain \
 && chmod -R a+rX,go-w /opt/dooservice

COPY entrypoint.sh /dooservice-entrypoint.sh
RUN chmod +x /dooservice-entrypoint.sh

USER dooservice
ENTRYPOINT ["/dooservice-entrypoint.sh"]
CMD ["odoo"]
