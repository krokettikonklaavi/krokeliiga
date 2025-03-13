FROM python:3.13-slim

WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
COPY . /bot
ENTRYPOINT ["python"]
CMD ["/bot/krokebot.py"]
