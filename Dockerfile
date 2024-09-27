FROM python:3.12-alpine

WORKDIR /bot

COPY . .

RUN pip install -r requirements.txt

CMD ["python3.12", "bot.py"]