FROM python:3.11-slim

# Install minimal TeX packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-fonts-recommended \
      latexmk && \
    rm -rf /var/lib/apt/lists/*


# Create a virtual environment in /venv
RUN python -m venv /venv

# Make sure the shell uses our virtual environment
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python deps
COPY require.txt /app/
RUN pip install --no-cache-dir -r /app/require.txt

# Copy code
COPY . /app
WORKDIR /app

# Configure logging
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=debug

# Start command
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]