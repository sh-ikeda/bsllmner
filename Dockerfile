FROM ollama/ollama:0.3.11
# FROM ollama/ollama:0.1.38

RUN apt update
RUN apt install -y python3.10
RUN apt install -y pip
RUN pip3 install ollama
RUN mkdir /app

COPY . /app/bsllmner/
WORKDIR /app/bsllmner/

ENTRYPOINT ["/bin/ollama"]
CMD ["serve"]

