import os

# ============================================================
# GUNICORN PRODUCTION CONFIGURATION FOR RENDER & CLOUD
# ============================================================

# Automatically binds to Render's dynamic PORT (Render assigns PORT=10000 by default)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Free-tier memory optimization:
# 1 worker process with 4 threads shares model and dataset memory in a single process space.
# This prevents multi-process RAM multiplication and guarantees the app stays well under
# Render's 512 MB Free Tier limit, eliminating SIGKILL / OOM worker crashes (HTTP 502).
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
keepalive = 5

# Stream logs directly to stdout/stderr for Render live logging console
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
