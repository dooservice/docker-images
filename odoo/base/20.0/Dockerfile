# Odoo 20.0 built from source, because there is no official odoo:20.0 image or nightly
# package yet. It follows the official odoo/docker 19.0 recipe step by step and reproduces
# the layout the Debian package installs, so everything built on top of it — the dooservice
# image, its CLI patches and the operator's odoo-bin wrapper — finds Odoo where it would
# find the official one. When the official image is published, dooservice-odoo:20.0 goes
# back to FROM odoo:20.0 and this directory is removed.

FROM ubuntu:noble

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV LANG=en_US.UTF-8

ARG TARGETARCH

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        adduser \
        ca-certificates \
        curl \
        dirmngr \
        fonts-dejavu-core \
        fonts-font-awesome \
        fonts-inconsolata \
        fonts-noto-cjk \
        fonts-roboto-unhinted \
        gnupg \
        gsfonts \
        libssl-dev \
        node-less \
        python3-asn1crypto \
        python3-babel \
        python3-cbor2 \
        python3-chardet \
        python3-cryptography \
        python3-dateutil \
        python3-docutils \
        python3-freezegun \
        python3-geoip2 \
        python3-gevent \
        python3-greenlet \
        python3-h11 \
        python3-idna \
        python3-jinja2 \
        python3-ldap \
        python3-libsass \
        python3-lxml \
        python3-lxml-html-clean \
        python3-magic \
        python3-markupsafe \
        python3-num2words \
        python3-odf \
        python3-ofxparse \
        python3-openpyxl \
        python3-openssl \
        python3-passlib \
        python3-pdfminer \
        python3-phonenumbers \
        python3-pil \
        python3-pip \
        python3-polib \
        python3-psutil \
        python3-psycopg2 \
        python3-pyldap \
        python3-pypdf2 \
        python3-qrcode \
        python3-renderpm \
        python3-reportlab \
        python3-requests \
        python3-rjsmin \
        python3-setuptools \
        python3-slugify \
        python3-stdnum \
        python3-urllib3 \
        python3-vobject \
        python3-watchdog \
        python3-werkzeug \
        python3-xlrd \
        python3-xlsxwriter \
        python3-xlwt \
        python3-zeep \
        xz-utils && \
    if [ -z "${TARGETARCH}" ]; then \
        TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    WKHTMLTOPDF_ARCH=${TARGETARCH} && \
    case ${TARGETARCH} in \
    "amd64") WKHTMLTOPDF_ARCH=amd64 && WKHTMLTOPDF_SHA=967390a759707337b46d1c02452e2bb6b2dc6d59  ;; \
    "arm64")  WKHTMLTOPDF_SHA=90f6e69896d51ef77339d3f3a20f8582bdf496cc  ;; \
    esac \
    && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_${WKHTMLTOPDF_ARCH}.deb \
    && echo ${WKHTMLTOPDF_SHA} wkhtmltox.deb | sha1sum -c - \
    && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
    && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ noble-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends nodejs npm \
    && npm install -g rtlcss \
    && apt-get purge --autoremove -y npm \
    && rm -rf /var/lib/apt/lists/*

ENV ODOO_VERSION=20.0
ARG ODOO_COMMIT=31474fded22ad65ece7cbe7d4d27c9ba8142d228
RUN curl -fsSL "https://github.com/odoo/odoo/archive/${ODOO_COMMIT}.tar.gz" -o /tmp/odoo.tar.gz \
    && mkdir /tmp/odoo \
    && tar -xzf /tmp/odoo.tar.gz -C /tmp/odoo --strip-components=1 \
    && cp -r /tmp/odoo/addons/* /tmp/odoo/odoo/addons/ \
    && mv /tmp/odoo/odoo /usr/lib/python3/dist-packages/odoo \
    && install -m 755 /tmp/odoo/setup/odoo /usr/bin/odoo \
    && rm -rf /tmp/odoo /tmp/odoo.tar.gz \
    && python3 -c "import odoo.release as r; assert r.serie == '20.0', r.serie" \
    && adduser --system --home /var/lib/odoo --quiet --group odoo \
    && mkdir -p /etc/odoo /var/log/odoo \
    && chown odoo:odoo /var/lib/odoo /var/log/odoo

COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

RUN chmod +x /entrypoint.sh \
    && chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

EXPOSE 8069 8071 8072

ENV ODOO_RC=/etc/odoo/odoo.conf

COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py
RUN chmod +x /usr/local/bin/wait-for-psql.py

USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
