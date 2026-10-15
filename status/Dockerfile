FROM python:3.13-alpine

COPY dooservice_status /app/dooservice_status

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 65534:65534
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/_dooservice/health', timeout=2)" || exit 1

CMD ["python", "-m", "dooservice_status"]
