FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install watchdog  # Required for watchmedo

CMD [ "python3", "-m", "app.presentation.telegram" ]
