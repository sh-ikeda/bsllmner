FROM python:3.10-alpine

RUN pip3 install ollama yaml
RUN apk update && \
    apk add git

RUN mkdir /app
WORKDIR /app
RUN git clone https://github.com/sh-ikeda/bsllmner.git
WORKDIR /app/bsllmner

ENTRYPOINT ["python3", "-m", "bsllmner"]
CMD ["-h"]
