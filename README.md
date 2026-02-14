# TFM - Prompt Injection en entornos corporativos

Entorno controlado para estudiar vulnerabilidades de prompt injection en LLMs y evaluar mitigaciones.

## Ejecutar `demo.ipynb` desde cero (tras clonar)

### 1) Requisitos
- Python 3.10+
- Ollama instalado y en ejecución (`http://127.0.0.1:11434`)
- Un modelo disponible en Ollama (por ejemplo `llama3.1:8b`)

### 2) Clonar y crear entorno
```bash
git clone <URL_DEL_REPO>
cd tfm
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 3) Preparar la base de datos local
```bash
python create_db.py
python populate_db.py
```

### 4) Levantar el backend
En otra terminal (con el mismo entorno activado):
```bash
python orchestrator.py
```
El backend quedará en `http://127.0.0.1:9000`.

### 5) Abrir y ejecutar el notebook
Abre `demo.ipynb` y ejecuta las celdas en orden.

### Ejecutar en Google Colab
- Abre `demo.ipynb` desde GitHub en Colab.
- La primera celda detecta Colab y clona el repositorio en `/content/tfm` si hace falta.
- Define `ORCHESTRATOR_BASE` apuntando a un backend accesible desde Colab (por defecto usa `http://127.0.0.1:9000`, que en Colab normalmente no aplica).
  - Ejemplo en una celda previa: `%env ORCHESTRATOR_BASE=https://abc123.ngrok-free.app`
- Ejecuta las celdas en orden.

Opcionalmente, puedes fijar el modelo antes de abrir el notebook:
```bash
export ORCHESTRATOR_MODEL=llama3.1:8b
```

## Variables de entorno (opcionales)
- `ORCHESTRATOR_ALLOW_ORIGINS`: CORS del backend (por defecto `*`).
- `OLLAMA_BASE_URL`: URL de Ollama (por defecto `http://127.0.0.1:11434`).
- `DEFAULT_MODEL`: modelo por defecto del backend.
- `CLASSIFICATION_MODEL`: modelo para clasificación de ruta.
- `OLLAMA_AUTO_PULL`: `true/false`, descarga automática si falta modelo.
- `ORCHESTRATOR_URL`: URL del endpoint para tests (`/orchestrate`).
- `ORCHESTRATOR_MODEL`: modelo usado por notebook/tests.

## Estructura relevante
- Backend: `orchestrator.py`
- Integración LLM: `llm_funct.py`
- Base de datos: `create_db.py`, `populate_db.py`
- Notebook demo: `demo.ipynb`
- Tests seguridad: `tests/run_safety_tests.py`, `tests/plot_safety_matrix.py`
