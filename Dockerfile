FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/back

WORKDIR /usr/src/back
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/

COPY alembic.ini ./
COPY ./src/main.py .

CMD ["python", "./main.py"]