FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY scrapper_scanbackup ./scrapper_scanbackup

RUN pip install --no-cache-dir .

# ScrapperSetting resuelve config.yml y exporter.dir contra SCANBACKUP_HOME
# (scrapper_scanbackup/utils/config/paths.py); aquí apunta a /app.
ENV SCANBACKUP_HOME=/app

RUN useradd --create-home --shell /bin/bash scanbackup \
    && chown -R scanbackup:scanbackup /app
USER scanbackup

ENTRYPOINT ["scanbackup"]
CMD ["run"]
