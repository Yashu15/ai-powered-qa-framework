# AI QA Automation Demo

This project contains two related but separate testing demos. The Booking.com
browser test is the current end-to-end example; `app/main.py` is sample logic
used by the separate unit-test generation agent and is not part of Booking.com.

## Files

- `playwright_agent.py`: runs a verified Booking.com smoke test in a Docker
  container and prints the pytest result. Its current execution path uses the
  known-good fallback test.
- `test_booking.py`: standalone Playwright smoke test that opens Booking.com,
  finds the destination field, enters Perth, and checks the field value.
- `ai_agent.py`: uses Ollama and LangChain to generate and retry pytest unit
  tests for the sample functions in `app/main.py`.
- `app/main.py`: sample discount and name-formatting functions for the separate
  unit-test demo; it is unrelated to the Booking.com test.
- `app/Dockerfile`: defines the shared container image with pytest and
  Playwright dependencies.
- `report.html` and `app/report.html`: generated pytest reports, not source
  files; they are excluded from Git.

## Requirements

- Python and the packages in `requirements.txt` on the host
- Docker Desktop running
- Ollama with the `llama3` model installed to run `ai_agent.py`

Install the host dependencies and build the test image from the project root:

```sh
python -m pip install -r requirements.txt
docker build -t target-app:latest app
```

Run the Booking.com smoke test through the Docker agent:

```sh
python playwright_agent.py
```

Or run the standalone test directly in the same Docker image:

```sh
docker run --rm -v "$PWD":/app -w /app target-app:latest \
  pytest -v test_booking.py --html=report.html --self-contained-html
```

Run the separate AI-generated unit-test demo:

```sh
python ai_agent.py
```

The browser test requires network access to Booking.com. Its live UI can vary
by region, locale, or site changes, so the test deliberately checks only that
the destination field is usable rather than asserting search-result details.