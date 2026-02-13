FROM python:3.11-slim

LABEL maintainer="Always-On AI Assistant"
LABEL description="Web documentation interface for the Always-On AI Assistant"

WORKDIR /app

# Install web dependencies only (lightweight)
COPY web/requirements.txt /app/web/requirements.txt
RUN pip install --no-cache-dir -r web/requirements.txt

# Copy the web app
COPY web/ /app/web/

# Copy documentation and config files
COPY USER_GUIDE.md /app/
COPY README.md /app/
COPY assistant_config.yml /app/

# Copy optional assets
COPY images/ /app/images/

ENV PORT=8080
ENV FLASK_DEBUG=false
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/status')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--access-logfile", "-", "web.app:app"]
