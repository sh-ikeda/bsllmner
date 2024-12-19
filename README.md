# bsllmner
Named Entity Recogniton (NER) of biological terms in BioSample records using LLMs

## Usage
### Setup ollama
See also the [documentation by ollama](https://hub.docker.com/r/ollama/ollama)
```sh
docker pull ollama/ollama:0.5.4
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:0.5.4
docker exec ollama ollama pull llama3.1:70b
```

### Setup Docker network to enable access to ollama from other containers
```sh
docker network create network_ollama
docker network connect network_ollama ollama
```

### Prepare bsllmner
```sh
docker pull shikeda/bsllmner:0.2.0
```

### Extraction task
```sh
docker run --rm --network network_ollama -v `pwd`:/data/ shikeda/bsllmner:0.2.0 -m llama3.1:70b -i 5,2,6,7 -v -u http://ollama:11434 extract /data/input.json
```
- `-m llama3.1:70b`: Specify LLM model
- `-i 5,2,6,7`: Specify prompts
- `-v`: When specified, displays progress
- `-u http://ollama:11434`: URL of ollama server
- `extract`: Extraction task mode
- `/data/input.json`: input json


### Review task
```sh
docker run --rm --network network_ollama -v `pwd`:/data/ shikeda/bsllmner:0.2.0 -m llama3:8b -i 5,2,6,7,14 -r /data/metasraout.tsv -l /data/llmout.tsv -u http://ollama:11434 review /data/input.json
```
- `-i 5,2,6,7,14`: Specify prompts
- `-r /data/metasraout.tsv`: Specify TSV file output by MetaSRA
- `-l /data/llmout.tsv`: Specify TSV file output by extraction task of `bsllmner`
- `review`: Review task mode
- `/data/input.json`: input json
