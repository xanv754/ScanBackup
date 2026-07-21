FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY scanbackup ./scanbackup

RUN pip install --no-cache-dir .

ENV SCANBACKUP_HOME=/app
ENV PYTHONUNBUFFERED=1

ARG UID=1000
ARG GID=1000
RUN groupadd --gid "$GID" scanbackup \
    && useradd --uid "$UID" --gid "$GID" --create-home --shell /bin/bash scanbackup \
    && chown -R scanbackup:scanbackup /app
USER scanbackup

ENTRYPOINT ["python", "-m", "scanbackup"]
CMD ["--help"]
