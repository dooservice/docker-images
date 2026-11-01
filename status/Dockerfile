FROM python:3.13-alpine@sha256:7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8

# The page runs on the standard library alone: pip, and the msgpack, urllib3 and setuptools
# it vendors, would only be code nobody runs and advisories nobody needs.
RUN python -m pip uninstall --yes --no-cache-dir --root-user-action=ignore pip \
 && ! python -c "import pip" 2>/dev/null

COPY dooservice_status /app/dooservice_status
COPY locales/ /app/locales/

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/_dooservice/health', timeout=2)"]

CMD ["python", "-m", "dooservice_status"]
