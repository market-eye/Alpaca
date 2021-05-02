FROM python:3.7.9
RUN apt-get update && apt-get install -y dnsutils
COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN useradd --create-home alpaca
WORKDIR /home/alpaca
USER alpaca
 
COPY alpaca-bot.py .
COPY alpaca_db.py .

ENTRYPOINT [ "python3", "alpaca-bot.py" ]
