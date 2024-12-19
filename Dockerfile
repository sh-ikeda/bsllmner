FROM python:3.10-alpine

RUN pip3 install ollama
RUN mkdir /app

COPY . /app/bsllmner/
WORKDIR /app/bsllmner/

ENTRYPOINT ["python3", "-m", "bsllmner"]
CMD ["-h"]
