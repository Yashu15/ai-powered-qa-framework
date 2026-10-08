# Shared pytest and Playwright runtime used to execute tests in isolation.
FROM mcr.microsoft.com/playwright/python:v1.63.0-jammy

WORKDIR /app

# Install pytest plugins
RUN pip install --no-cache-dir pytest-playwright pytest-html

# Default execution command
CMD ["pytest"]