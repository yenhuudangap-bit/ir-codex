# Codex de Relações Internacionais

Este projecto cria um pipeline completo para transformar o livro **International Relations Theory** da E-IR em conteúdos totalmente localizados para português. O processo abrange a extracção de capítulos numerados, limpeza tipográfica, tradução, enriquecimento com palavras-chave bilíngues e publicação em PDF.

## Pré-requisitos

* Python 3.11 ou superior.
* Ambiente virtual recomendado (`python -m venv .venv`).
* Ligação à Internet na primeira execução para descarregar o modelo de tradução Hugging Face.

Instala as dependências de execução:

```bash
python -m venv .venv
source .venv/bin/activate  # No Windows usa `.venv\\Scripts\\activate`
pip install -r requirements.txt
```

## Estrutura do pipeline

O ficheiro [`codex.yml`](codex.yml) define as quatro tarefas principais:

1. **extract** – extrai os capítulos numerados do PDF (`data/International-Relations-Theory-E-IR.pdf`), remove hifenizações e guarda o texto limpo em inglês.
2. **translate** – traduz integralmente cada capítulo para português europeu.
3. **keywords** – calcula palavras-chave com RAKE, traduz cada termo para português e acrescenta a linha `Palavras-chave: ...` no final de cada capítulo.
4. **pdf** – gera PDFs individuais por capítulo e um PDF compilado com índice formatado.

Podes executar cada etapa individualmente ou tudo de uma vez pelo utilitário principal `run_pipeline.py`:

```bash
# Executa todas as etapas em sequência
python run_pipeline.py all

# Executa apenas uma etapa específica
python run_pipeline.py extract
python run_pipeline.py translate
python run_pipeline.py keywords
python run_pipeline.py pdf
```

### Utilização avançada

* Para usar um PDF alternativo apenas na fase de extracção, indica o caminho através de `--pdf`: `python run_pipeline.py extract --pdf caminho/ficheiro.pdf`.
* O parâmetro `--log-level` permite obter mais detalhes (`DEBUG`, `INFO`, `WARNING`, ...).

## Saídas geradas

Depois de concluído, os resultados são guardados em `output/` com a seguinte organização:

```
output/
  chapters.json           # Metadados completos de cada capítulo
  chapters_en/            # Texto limpo em inglês (ficheiros .txt)
  chapters_pt/            # Tradução para português com palavras-chave (ficheiros .txt)
  pdf/
    capitulos/            # PDFs individuais por capítulo
    compilado.pdf         # Versão completa com índice
```

Cada ficheiro `.txt` em português termina com a secção `Palavras-chave`, onde os termos aparecem em português seguidos do original em inglês entre parênteses.

## Observações técnicas

* A tradução utiliza o modelo `Helsinki-NLP/opus-mt-en-pt` através da biblioteca `transformers`. A primeira execução pode demorar devido ao download do modelo e ao carregamento em memória.
* A extracção de capítulos baseia-se na detecção de cabeçalhos numerados do PDF original. Caso uses uma versão diferente do livro, confirma se os cabeçalhos seguem o mesmo padrão.
* O gerador de palavras-chave aplica uma versão simplificada do algoritmo RAKE e pode ser ajustado em `src/ir_codex/keywords.py` se desejares mais ou menos termos por capítulo.

## Desenvolvimento

O código-fonte principal vive em `src/ir_codex/`. As principais componentes são:

* `extractor.py` – leitura do PDF e segmentação por capítulos.
* `cleaner.py` – normalização de linhas e remoção de hifenizações.
* `translator.py` – serviço de tradução reutilizável.
* `keywords.py` – cálculo e tradução de palavras-chave.
* `pdf_builder.py` – criação dos PDFs individuais e do compilado com índice.
* `pipeline.py` – orquestração das etapas e gestão de ficheiros intermédios.

Os logs informam o progresso de cada fase, ajudando a monitorizar capítulos processados e ficheiros criados.

## Licença

Este projecto serve fins educativos e respeita os direitos do material de origem. Verifica a licença da obra original antes de redistribuir os conteúdos traduzidos.
