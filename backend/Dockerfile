FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY seed_demo.py ./seed_demo.py
COPY run.py ./run.py

CMD ["python", "run.py"]
