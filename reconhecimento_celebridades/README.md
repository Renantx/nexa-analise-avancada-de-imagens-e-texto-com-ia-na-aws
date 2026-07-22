# Reconhecimento Celebridades

Projeto usado para exemplificar o uso do [AWS Rekognition](https://docs.aws.amazon.com/pt_br/rekognition/latest/APIReference/API_RecognizeCelebrities.html) no reconhecimento dos rostos de celebridades.

## Pré-requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Conta AWS com permissão `rekognition:RecognizeCelebrities`

## Instalação

```sh
uv sync
```

## Execução

```sh
uv run main.py
```

Por padrão analisa `bbc.jpg`, `msn.jpg` e `neymar-torcedores.jpg`.

Opções:

```sh
uv run main.py --images images/bbc.jpg images/msn.jpg
uv run main.py --confidence 85 --region us-east-1
```

A anotação usa uma fonte do sistema quando disponível; caso contrário, cai no default do Pillow (portável entre Windows/macOS/Linux).

Imagens geradas (`*-resultado.jpg`) ficam locais e são ignoradas pelo Git.
