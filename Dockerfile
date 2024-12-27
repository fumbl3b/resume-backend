FROM python:3.11-slim

# Install minimal TeX packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      texlive-latex-base \
      texlive-latex-recommended \
      texlive-fonts-recommended \
      latexmk && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY . /app
WORKDIR /app

# Start command
CMD ["gunicorn", "app:app"]