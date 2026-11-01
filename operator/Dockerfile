# The operator: the Odoo image of an environment, plus what a person or an AI agent
# needs to work on it — a shell, psql, git, Claude Code, opencode and the `dooservice`
# command. One is started per console session, next to the environment's own Odoo
# container, and removed when the session ends.
#
# It never runs Odoo as a service. The environment's container does that; this one
# only runs `odoo-bin -u`, `odoo-bin shell` and tests against the same database, with
# the same addons, as the same user (uid 1500) so files it writes are files the agent
# can still manage.
#
# `dooservice-odoo` is the Odoo image of the same build, which docker-bake.hcl passes in.
FROM dooservice-odoo

ARG ODOO_VERSION
ARG CLAUDE_CODE_VERSION=2.1.295
ARG OPENCODE_VERSION=1.18.35
ARG RTK_VERSION=0.48.0
ARG RTK_SHA256=e4e650fa1677c0de2f6839a6040d7b17f312d32f163c402b75af70e9e5af1a91

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git less vim-tiny procps tini postgresql-client \
 && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN mkdir -p /opt/ai \
 && HOME=/tmp/claude-install bash -o pipefail -c "curl -fsSL https://claude.ai/install.sh | bash -s ${CLAUDE_CODE_VERSION}" \
 && install -m 755 "$(readlink -f /tmp/claude-install/.local/bin/claude)" /opt/ai/claude \
 && HOME=/tmp/opencode-install bash -o pipefail -c "curl -fsSL https://opencode.ai/install | bash -s -- --version ${OPENCODE_VERSION} --no-modify-path" \
 && install -m 755 /tmp/opencode-install/.opencode/bin/opencode /opt/ai/opencode \
 && curl -fsSL -o /tmp/rtk.tar.gz "https://github.com/rtk-ai/rtk/releases/download/v${RTK_VERSION}/rtk-x86_64-unknown-linux-musl.tar.gz" \
 && echo "${RTK_SHA256}  /tmp/rtk.tar.gz" | sha256sum -c - \
 && tar -xzf /tmp/rtk.tar.gz -C /opt/ai rtk \
 && chmod 755 /opt/ai/rtk \
 && ln -s /opt/ai/rtk /usr/local/bin/rtk \
 && rm -rf /tmp/claude-install /tmp/opencode-install /tmp/rtk.tar.gz

COPY rootfs/ /
COPY locales/ /opt/dooservice/locales/
COPY skills/odoo/${ODOO_VERSION}/ /opt/dooservice/ai/skills/code/
COPY skills/odoo/common/ /opt/dooservice/ai/skills/code/
ENV PYTHONPATH=/opt/dooservice/lib

# Files keep the mode git gives them, executables included: here everyone may read them and
# nobody but root may change them.
RUN chmod -R a+rX,go-w /opt/dooservice /etc/profile.d/dooservice.sh /etc/gitconfig \
      /usr/local/bin/claude /usr/local/bin/opencode /usr/local/bin/odoo-bin /usr/local/bin/dooservice \
      /usr/local/bin/psql \
 && mkdir -p /home/dooservice \
 && chown dooservice:dooservice /home/dooservice \
 && usermod -d /home/dooservice dooservice \
 && python3 -m dooservice_console.build \
 && chmod -R a+rX /opt/dooservice/opencode-config

ENV ODOO_VERSION=${ODOO_VERSION} \
    DISABLE_AUTOUPDATER=1 \
    TERM=xterm-256color \
    COLORTERM=truecolor \
    LANG=C.UTF-8 \
    HOME=/home/dooservice

USER dooservice
WORKDIR /mnt/addons
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sleep", "infinity"]
