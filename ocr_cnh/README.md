# OCR CNH

Projeto usado para exemplificar o uso do [AWS Textract](https://docs.aws.amazon.com/pt_br/textract/latest/dg/API_AnalyzeDocument.html) na extração de dados da Carteira Nacional de Trânsito (CNH).

## Pré-requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- Conta AWS com permissão `textract:AnalyzeDocument`

## Instalação

```sh
uv sync
```

Para desenvolvimento (testes):

```sh
uv sync --group dev
```

## Execução

```sh
uv run main.py
```

Opções:

```sh
uv run main.py --image images/cnh.png --region us-east-1
uv run main.py --force   # ignora o cache local response.json
```

Na primeira execução (ou com `--force`), a API é chamada e o resultado é salvo em `response.json` (arquivo local, ignorado pelo Git). Nas execuções seguintes, o cache é reutilizado.

## Testes

```sh
uv run pytest
```

Os testes usam a fixture em `fixtures/textract_response.json` e **não** chamam a AWS.

## Privacidade

A imagem de CNH e a resposta do Textract podem conter dados pessoais. Não compartilhe `response.json` gerado localmente.
