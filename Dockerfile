FROM python:3
WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ="Europe/Paris"
COPY . /app
CMD [ "python", "/app/bot.py" ]