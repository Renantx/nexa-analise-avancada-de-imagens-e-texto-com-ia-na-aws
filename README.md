# Nexa - Análise Avançada de Imagens e Texto com IA na AWS

Contém os projetos desenvolvidos durante o curso **Nexa - Análise Avançada de Imagens e Texto com IA na AWS**.

Os scripts rodam **localmente** com [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), enviando bytes da imagem para as APIs do **Amazon Textract** e **Amazon Rekognition**.

## Projetos

| Projeto | Serviço | API |
|---------|---------|-----|
| [OCR CNH](./ocr_cnh/) | Textract | `AnalyzeDocument` (FORMS) |
| [OCR Lista Escolar](./ocr_lista_escolar/) | Textract | `DetectDocumentText` |
| [Reconhecimento de Atacantes](./reconhecimento_atacantes/) | Rekognition | `CompareFaces` |
| [Reconhecimento de Celebridades](./reconhecimento_celebridades/) | Rekognition | `RecognizeCelebrities` |

## Pré-requisitos

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/)
- Conta AWS com credenciais configuradas (`aws configure` ou variáveis de ambiente)
- Região definida via `AWS_DEFAULT_REGION` / `AWS_REGION` ou `--region`

## Configuração IAM (mínimo)

Crie um usuário/role com políticas restritas ao que cada demo precisa:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TextractDemos",
      "Effect": "Allow",
      "Action": [
        "textract:AnalyzeDocument",
        "textract:DetectDocumentText"
      ],
      "Resource": "*"
    },
    {
      "Sid": "RekognitionDemos",
      "Effect": "Allow",
      "Action": [
        "rekognition:CompareFaces",
        "rekognition:RecognizeCelebrities"
      ],
      "Resource": "*"
    }
  ]
}
```

> As APIs Textract/Rekognition cobram por chamada. Prefira o cache local dos projetos OCR e evite `--force` sem necessidade.

## Privacidade

- Imagens de documento (ex.: CNH) e respostas da API podem conter **PII**.
- O arquivo `response.json` gerado em tempo de execução **não é versionado** (está no `.gitignore`).
- Fixtures em `*/fixtures/` existem apenas para testes offline — trate-as com cuidado ao compartilhar o repositório.

## Melhorias aplicadas

Em relação à versão original do curso, este repositório passou pelas seguintes melhorias:

### Correções

- **Cache OCR**: na primeira execução (sem `response.json`), a API é chamada e o resultado é **relido imediatamente** — antes o script seguia com lista vazia.
- **Paths absolutos**: cache e imagens usam `Path(__file__).resolve().parent`, funcionando de qualquer diretório de trabalho.
- **Fonte portátil**: anotação de imagens tenta fontes comuns do sistema e faz fallback para `ImageFont.load_default()` (sem depender de `Ubuntu-R.ttf`).

### Robustez e DX

- Tratamento de `ClientError` / `BotoCoreError` e validação de arquivo inexistente em todos os scripts.
- **CLI com `argparse`**: `--image`, `--images`, `--source`, `--target`, `--threshold`, `--confidence`, `--region`, `--force`, `--output`.
- Região AWS configurável por ambiente (`AWS_DEFAULT_REGION` / `AWS_REGION`) ou flag `--region`.
- Descrições reais nos `pyproject.toml` (substituindo o placeholder do template).

### Qualidade e docs

- Testes unitários offline nos projetos OCR (`fixtures/textract_response.json` + `pytest`).
- READMEs de cada projeto atualizados (`uv sync`, exemplos de CLI, IAM).
- `.gitignore` ampliado para `response.json` e imagens `*-resultado.jpg` / `resultado_*.jpg`.
- Dependência do Pillow atualizada (`>=11.3.0`) para melhor compatibilidade com Python recente.

### Evoluções futuras (não implementadas)

- Pipeline S3 → Lambda → Textract/Rekognition
- IaC (SAM/CDK), CI/CD e monorepo `uv workspace`
- Biblioteca compartilhada para desenho de caixas / factory do client

## Como executar (padrão)

Em cada pasta de projeto:

```sh
uv sync
uv run main.py
```

Com opções (exemplos):

```sh
# OCR — forçar nova chamada à API
uv run main.py --force --region us-east-1

# Celebridades — imagem e limiar customizados
uv run main.py --images images/bbc.jpg --confidence 85

# Atacantes — comparar outras fotos
uv run main.py --source images/messi.jpg --target images/msn.jpg --threshold 75
```

Testes OCR (sem chamar a AWS):

```sh
cd ocr_cnh
uv sync --group dev
uv run pytest
```
