from typing import TypedDict, Any
import sqlite3
import time
import os
import json

from langgraph.graph import StateGraph, START, END

from llm_funct import classify_request_tool, generate_sql_tool
from prompts import prompts, system_messages, RUTAS, SENSITIVE_KEYWORDS

CLIENTS_PII = "clients_pii"


def _log_event(log_type: str, payload: dict):
    lg_dir = "logs"
    os.makedirs(lg_dir, exist_ok=True)
    path = os.path.join(lg_dir, "logs.jsonl")

    record = {
        "type": log_type,
        "timestamp": time.time(),
        **payload,
    }

    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _clean_sql_info(table_name: str, columns: list[tuple]) -> list[tuple]:
    if (table_name or "").lower() == CLIENTS_PII:
        return []
    safe_columns = [
        col for col in columns
        if not any(n in (col[1] or "").lower() for n in SENSITIVE_KEYWORDS)
    ]
    return safe_columns

class OrchestrationState(TypedDict, total=False):
    payload: dict[str, Any] #prompt original, modelo, etc
    prompt: str
    session_id: str
    full_conv: list[dict] #contexto
    route: str
    db_prompt: str
    sql_query: str
    query_results: str


async def classify_node(state: OrchestrationState) -> dict[str, Any]:
    prompt = state.get("prompt", "") or ""
    prompt_l = prompt.lower()
    payload = state.get("payload", {}) or {}
    model_name = payload.get("classification_model") or payload.get("model")

    if any(keyword in prompt_l for keyword in SENSITIVE_KEYWORDS):
        _log_event("sensitive_info_detected", {"prompt": prompt})
        return {"route": "malicious_request"}

    try: # llamada a  herramienta de routing
        cl = await classify_request_tool.ainvoke({
            "prompt": prompt,
            "model": model_name,
        })
        cl = (cl or "").strip()
        if cl not in RUTAS:
            cl = "simple_request"
        return {"route": cl}
    except Exception:
        return {"route": "simple_request"}


async def db_schema_node(state: OrchestrationState) -> dict[str, Any]:
    db_path = "clients.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    db_prompt = ""
    initial_query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(initial_query)
    tables = cursor.fetchall()

    for t in tables:
        t_name = t[0]
        cursor.execute(f"PRAGMA table_info({t_name});")
        columns = cursor.fetchall()
        safe_columns = _clean_sql_info(t_name, columns) # limpiar columnas de pii
        if not safe_columns:
            continue
        col_string = ", ".join([f"{col[1]} {col[2]}" for col in safe_columns])
        t_info = f"Table {t_name} ({col_string})"
        context = f"Database Schema:\n{t_info}\n"
        db_prompt += "\n" + context
    conn.close()
    return {"db_prompt": db_prompt}

# usar macro
async def generate_sql_node(state: OrchestrationState) -> dict[str, Any]:
    try:
        full_conv = state.get("full_conv", [])
        if len(full_conv) > 6:
            full_conv = full_conv[-6:]
        sql_query = await generate_sql_tool.ainvoke({
            "prompt": state.get("prompt", ""),
            "db_schema": state.get("db_prompt", ""),
            "conv": full_conv,
        })
    except Exception:
        sql_query = ""
    return {"sql_query": sql_query}


async def exec_sql_node(state: OrchestrationState) -> dict[str, Any]:
    db_path = "clients.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sql_query = state.get("sql_query", "")

    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        result_str = f"{results}"
    except Exception as e:
        result_str = f"SQL Execution Error: {str(e)}"
    finally:
        conn.commit()
        conn.close()
    return {"query_results": result_str}


async def finalize_node(state: OrchestrationState) -> dict[str, Any]:
    payload = dict(state.get("payload", {}))

    if state.get("route") == "needs_db_access":
        payload["prompt"] = prompts["final_db_prompt"].format(
            db_schema=state.get("db_prompt", ""),
            sql_query=state.get("sql_query", ""),
            query_results=state.get("query_results", ""),
            prompt=state.get("prompt", ""),
        )

    # ampliar informacion dinamica
    payload["system"] = system_messages["system_final_response"].format(
        current_date=time.strftime("%Y-%m-%d")
    )

    return {"payload": payload}


def error_node(state: OrchestrationState) -> dict[str, Any]:
    payload = dict(state.get("payload", {}))
    payload["prompt"] = prompts["malicious_request_prompt"].format(
        prompt=state.get("prompt", "")
    )
    payload["system"] = system_messages["system_final_response"].format(
        current_date=time.strftime("%Y-%m-%d")
    )
    return {"payload": payload}


def route_from_classification(state: OrchestrationState) -> str:
    return state.get("route", "simple_request")


main_graph = StateGraph(OrchestrationState)

main_graph.add_node("classification", classify_node)
main_graph.add_node("db_schema", db_schema_node)
main_graph.add_node("sql_query", generate_sql_node)
main_graph.add_node("query_results", exec_sql_node)
main_graph.add_node("finalize", finalize_node)
main_graph.add_node("error_node", error_node) # de malicious request

main_graph.add_edge(START, "classification")
main_graph.add_conditional_edges(
    "classification",
    route_from_classification,
    {
        "malicious_request": "error_node", 
        "needs_db_access": "db_schema",
        "simple_request": "finalize"
    },
)
main_graph.add_edge("db_schema", "sql_query")
main_graph.add_edge("sql_query", "query_results")
main_graph.add_edge("query_results", "finalize")
main_graph.add_edge("finalize", END) # finalizar en streaming
main_graph.add_edge("error_node", END) # finalizar en streaming

graph = main_graph.compile()