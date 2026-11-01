# Odoo's official image, plus the dooservice user, the patched `odoo db` command, the
# Dooservice addons and an entrypoint that installs the addons' Python requirements.
# Built with `docker buildx bake` (docker-bake.hcl at the repository's root).

ARG ODOO_VERSION=19.0
ARG ODOO_DIGEST
FROM odoo:${ODOO_VERSION}@${ODOO_DIGEST}

USER root

# The official images are not rebuilt for every security update of their release, and
# 16.0 and 17.0 no longer are at all: every build takes the updates itself. Odoo itself and
# wkhtmltopdf come from .deb files, not from a repository, so they never move.
# Debian 11, under Odoo 16.0, left security support in August 2026 and its security
# updates moved to the archive: from deb.debian.org they answer 404.
RUN . /etc/os-release \
 && if [ "${VERSION_CODENAME}" = "bullseye" ]; then \
      sed -i 's#http://deb.debian.org/debian-security#http://archive.debian.org/debian-security#' /etc/apt/sources.list; \
    fi \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# rtlcss, which Odoo runs to build right-to-left stylesheets, reinstalled where the official
# image put it with npm (16.0 and 17.0), so its postcss, nanoid and source-map-js are the
# latest releases of their ranges. 17.0 dropped npm after using it: it is added for this and
# removed again. The newer images take rtlcss from their distribution and are left as they are.
ARG RTLCSS_VERSION=4.3.0
RUN if [ -d /usr/local/lib/node_modules/rtlcss ]; then \
      added=""; \
      if ! command -v npm >/dev/null; then \
        apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends npm && added=npm; \
      fi; \
      rm -rf /usr/local/lib/node_modules/rtlcss /usr/local/bin/rtlcss \
      && npm install -g --prefix /usr/local "rtlcss@${RTLCSS_VERSION}" \
      && npm cache clean --force \
      && if [ -n "${added}" ]; then apt-get purge -y --auto-remove npm && rm -rf /var/lib/apt/lists/*; fi \
      && rtlcss --version; \
    fi

RUN groupadd -g 1500 dooservice \
 && useradd -u 1500 -g 1500 -d /var/lib/odoo -s /bin/bash dooservice \
 && mkdir -p /mnt/addons /mnt/backups \
 && chown -R dooservice:dooservice /var/lib/odoo /mnt/addons /etc/odoo \
 && chown dooservice:dooservice /mnt/backups

ARG ODOO_VERSION
COPY cli-patches/ /tmp/cli-patches/
RUN chmod +x /tmp/cli-patches/apply.sh \
 && /tmp/cli-patches/apply.sh ${ODOO_VERSION} \
 && rm -rf /tmp/cli-patches/

# The Dooservice addons, from dooservice/odoo-addons at the commit docker-bake.hcl pins for
# this version, on every environment's addons path. dooservice_connect is loaded as a
# server-wide module from odoo.conf and never installed.
ARG ADDONS_COMMIT
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN test -n "${ADDONS_COMMIT}" \
 && mkdir -p /tmp/dooservice-addons /opt/dooservice/addons \
 && curl -fsSL "https://codeload.github.com/dooservice/odoo-addons/tar.gz/${ADDONS_COMMIT}" \
      | tar -xz --strip-components=1 -C /tmp/dooservice-addons \
 && test -f /tmp/dooservice-addons/dooservice_connect/__manifest__.py \
 && mv /tmp/dooservice-addons/dooservice_connect /opt/dooservice/addons/dooservice_connect \
 && rm -rf /tmp/dooservice-addons \
 && chmod -R a+rX,go-w /opt/dooservice

COPY entrypoint.sh /dooservice-entrypoint.sh
RUN chmod +x /dooservice-entrypoint.sh

USER dooservice
ENTRYPOINT ["/dooservice-entrypoint.sh"]
CMD ["odoo"]
