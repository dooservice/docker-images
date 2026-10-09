# The operator: the Odoo image of an environment, plus what a person or an AI agent
# needs to work on it — a shell, psql, git, Claude Code, opencode and the `dooservice`
# command. One is started per console session, next to the environment's own Odoo
# container, and removed when the session ends.
#
# It never runs Odoo as a service. The environment's container does that; this one
# only runs `odoo-bin -u`, `odoo-bin shell` and tests against the same database, with
# the same addons, as the same user (uid 1500) so files it writes are files the agent
# can still manage.

ARG ODOO_VERSION=19.0
FROM ghcr.io/dooservice/dooservice-odoo:${ODOO_VERSION}

ARG ODOO_VERSION
ARG CLAUDE_CODE_VERSION=2.1.268
ARG OPENCODE_VERSION=1.18.30
ARG RTK_VERSION=0.48.0

USER root

# Debian 11, under Odoo 16.0, left security support in August 2026 and its security
# updates moved to the archive: from deb.debian.org they answer 404.
RUN . /etc/os-release \
 && if [ "${VERSION_CODENAME}" = "bullseye" ]; then \
      sed -i 's#http://deb.debian.org/debian-security#http://archive.debian.org/debian-security#' /etc/apt/sources.list; \
    fi

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git less vim-tiny procps tini postgresql-client \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ai \
 && HOME=/tmp/claude-install bash -c "curl -fsSL https://claude.ai/install.sh | bash -s ${CLAUDE_CODE_VERSION}" \
 && install -m 755 "$(readlink -f /tmp/claude-install/.local/bin/claude)" /opt/ai/claude \
 && HOME=/tmp/opencode-install bash -c "curl -fsSL https://opencode.ai/install | bash -s -- --version ${OPENCODE_VERSION} --no-modify-path" \
 && install -m 755 /tmp/opencode-install/.opencode/bin/opencode /opt/ai/opencode \
 && curl -fsSL "https://github.com/rtk-ai/rtk/releases/download/v${RTK_VERSION}/rtk-x86_64-unknown-linux-musl.tar.gz" \
      | tar -xz -C /opt/ai rtk \
 && chmod 755 /opt/ai/rtk \
 && ln -s /opt/ai/rtk /usr/local/bin/rtk \
 && rm -rf /tmp/claude-install /tmp/opencode-install

COPY rootfs/ /
RUN chmod 755 /usr/local/bin/claude /usr/local/bin/opencode /usr/local/bin/odoo-bin /usr/local/bin/dooservice \
 && chmod 644 /opt/dooservice/ai/* /opt/dooservice/lib/* /opt/dooservice/build/* /etc/profile.d/dooservice.sh \
 && mkdir -p /home/dooservice \
 && chown dooservice:dooservice /home/dooservice \
 && usermod -d /home/dooservice dooservice

RUN python3 /opt/dooservice/build/opencode_plugins.py \
 && chmod -R a+rX /opt/dooservice/opencode-config \
 && rm -rf /opt/dooservice/build

ENV ODOO_VERSION=${ODOO_VERSION} \
    DISABLE_AUTOUPDATER=1 \
    TERM=xterm-256color \
    COLORTERM=truecolor \
    LANG=C.UTF-8 \
    HOME=/home/dooservice \
    PYTHONPATH=/opt/dooservice/lib

USER dooservice
WORKDIR /mnt/extra-addons
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sleep", "infinity"]
