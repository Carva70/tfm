from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os
from typing import Any

from ollama import AsyncClient

from prompts import prompts, system_messages

load_dotenv()

#cambiar el .env
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qooba/qwen3-coder-30b-a3b-instruct:q3_k_m")
CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", DEFAULT_MODEL)
OLLAMA_AUTO_PULL = os.getenv("OLLAMA_AUTO_PULL", "false").lower() in {"1", "true", "yes"}

_READY_MODELS: set[str] = set()

print(OLLAMA_BASE_URL, DEFAULT_MODEL)


def _extract_model_names(tags_resp: Any) -> list[str]:
    models = []
    if isinstance(tags_resp, dict):
        models = tags_resp.get("models", [])
    else:
        models = getattr(tags_resp, "models", []) or []

    names = []
    for m in models:
        if isinstance(m, dict):
            name = m.get("name") or m.get("model")
        else:
            name = getattr(m, "name", None) or getattr(m, "model", None)
        if name:
            names.append(name)
    return names


async def get_ollama_runtime_status() -> dict[str, Any]:
    client = AsyncClient(host=OLLAMA_BASE_URL)
    try:
        tags_resp = await client.list()
        return {
            "ok": True,
            "base_url": OLLAMA_BASE_URL,
            "models": _extract_model_names(tags_resp),
            "auto_pull": OLLAMA_AUTO_PULL,
        }
    except Exception as e:
        return {
            "ok": False,
            "base_url": OLLAMA_BASE_URL,
            "models": [],
            "auto_pull": OLLAMA_AUTO_PULL,
            "error": str(e),
        }


async def ensure_ollama_model(model_name: str) -> None:
    if not model_name or model_name in _READY_MODELS:
        return

    client = AsyncClient(host=OLLAMA_BASE_URL)
    tags_resp = await client.list()
    available_models = set(_extract_model_names(tags_resp))

    if model_name not in available_models:
        if not OLLAMA_AUTO_PULL:
            raise RuntimeError(
                f"Modelo '{model_name}' no disponible en Ollama. "
                "Activa OLLAMA_AUTO_PULL=true o ejecútalo manualmente con 'ollama pull'."
            )
        await client.pull(model=model_name)

    _READY_MODELS.add(model_name)

def get_chat_model(model: str, streaming: bool = False) -> ChatOllama:
    #lang chain
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=model,
        temperature=0,
        streaming=streaming,
    )


def build_messages(conv: list[dict], system_prompt: str, prompt_override: str | None = None):
    messages = []
    if system_prompt:
        messages.append(SystemMessage(content=system_prompt))

    last_index = len(conv) - 1

    for idx, msg in enumerate(conv):
        role = msg["role"]
        content = msg["content"]
        if prompt_override is not None and idx == last_index and role == "user":
            content = prompt_override

        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))

    #agregar prompt al final
    if prompt_override is not None and (not conv or conv[-1]["role"] != "user"):
        messages.append(HumanMessage(content=prompt_override))

    return messages

#genera contexto de la generacion sql .
def format_conv(conv: list[dict]) -> str:
    formatted_conv = ""
    for msg in conv:
        role = msg["role"]
        content = msg["content"]
        formatted_conv += f"<{role.upper()}>\n{content}\n</{role.upper()}>\n\n"
    return formatted_conv


async def stream_from_ollama(payload, conv: list[dict]):
    model_name = payload.get("generation_model") or payload.get("model", DEFAULT_MODEL)
    system_prompt = payload.get("system", "")
    prompt = payload.get("prompt", "")

    try:
        await ensure_ollama_model(model_name)
        llm = get_chat_model(model_name, streaming=True)
        messages = build_messages(conv, system_prompt, prompt_override=prompt)
        async for chunk in llm.astream(messages):
            token = chunk.content or ""
            if token:
                #delta es un chunk (no todo el mensaje)
                yield token
    except Exception as e:
        yield f"\nError en el streaming: {str(e)}\n"


@tool("classify_request")
async def classify_request_tool(prompt: str, model: str | None = None) -> str:
    """clasificacion"""
    model_name = model or CLASSIFICATION_MODEL
    try:
        await ensure_ollama_model(model_name)
        llm = get_chat_model(model_name, streaming=False)
        messages = [
            SystemMessage(content=system_messages["system_route"]),
            HumanMessage(content=prompts["route_user_prompt"].format(prompt=prompt)),
        ]
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception:
        return "simple_request"


@tool("generate_sql")
async def generate_sql_tool(prompt: str, db_schema: str, conv: list[dict]) -> str:
    """generacion de consulta sql"""
    prompt_w_c = prompts["sql_generation_full_prompt"].format(
        conversation=format_conv(conv),
        db_schema=db_schema,
        prompt=prompt,
    )

    try:
        await ensure_ollama_model(DEFAULT_MODEL)
        llm = get_chat_model(DEFAULT_MODEL, streaming=False)
        messages = [
            SystemMessage(content=system_messages["system_sql_generation"]),
            HumanMessage(content=prompt_w_c),
        ]
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception:
        return ""
