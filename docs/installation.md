# Installation

## Requirements

- Python 3.10 or later.
- Neo4j 5.x.
- Streamlit.
- LLM API access through DeepSeek or Gemini.

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements_platform.txt
pip install -r requirements_extraction.txt
```

## Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Fill in:

```text
DEEPSEEK_API_KEY=
GEMINI_API_KEY=
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j
```

Use either DeepSeek or Gemini for extraction. The platform question-answering service uses the DeepSeek-compatible LLM wrapper by default.

## Neo4j

Start Neo4j before running the graph builder or interfaces. Create indexes and constraints through the graph builder workflow before loading data.

