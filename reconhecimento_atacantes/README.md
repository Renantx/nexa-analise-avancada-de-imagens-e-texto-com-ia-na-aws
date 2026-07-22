# Reconhecimento Atacantes

Projeto usado para exemplificar o uso do [AWS Rekognition](https://docs.aws.amazon.com/pt_br/rekognition/latest/APIReference/API_CompareFaces.html) na comparação de rostos entre fotos.

## Pré-requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Conta AWS com permissão `rekognition:CompareFaces`

## Instalação

```sh
uv sync
```

## Execução

```sh
uv run main.py
```

Por padrão compara `neymar.jpg` (origem) com `msn.jpg` (alvo).

Opções:

```sh
uv run main.py --source images/messi.jpg --target images/msn.jpg
uv run main.py --threshold 75 --region us-east-1
uv run main.py --output images/meu_resultado.jpg
```

Há imagens extras em `images/` (`cr7.jpg`, `bale.jpg`, `bbc.jpg`, etc.) para experimentar via CLI.

Imagens geradas (`resultado_*.jpg`) ficam locais e são ignoradas pelo Git.
