from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid
import os

import json
import time

load_dotenv()

from llm_funct import stream_from_ollama, get_ollama_runtime_status
from orch_graph import graph
from prompts import STREAM_SENSITIVE_TERMS, MALICIOUS_SHORT_RESPONSE_DEFAULT
from langchain_core.runnables.graph import CurveStyle, NodeStyles, MermaidDrawMethod

app = FastAPI(debug=True)

ORCHESTRATOR_ALLOW_ORIGINS = os.getenv("ORCHESTRATOR_ALLOW_ORIGINS", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ORCHESTRATOR_ALLOW_ORIGINS.split(",") if o.strip()],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def emit(event_type: str, payload: dict):
    return json.dumps({
        "type": event_type,
        "timestamp": time.time(),
        **payload,
    }) + "\n"

conv_store: dict[str, list[dict]] = {}

MAX_MESSAGES = 6
MALICIOUS_SHORT_RESPONSE = os.getenv("MALICIOUS_SHORT_RESPONSE", MALICIOUS_SHORT_RESPONSE_DEFAULT)


def _stream_contains_sensitive(buffer: str) -> bool:
    buf_l = buffer.lower()
    return any(term in buf_l for term in STREAM_SENSITIVE_TERMS)


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




async def orchestrated_stream(payload):

    prompt = payload.get("prompt", "")
    session_id = payload.get("session_id", str(uuid.uuid4()))
    if session_id == "":
        session_id = str(uuid.uuid4())
    if not payload.get("session_id"):
        yield emit("session_id", {"session_id": session_id})

    conv_store.setdefault(session_id, []).append({
        "role": "user",
        "content": prompt,
    })

    reduced_conv = conv_store.get(session_id, [])[-MAX_MESSAGES:]

    graph_state = {
        "payload": payload,
        "prompt": prompt,
        "session_id": session_id,
        "full_conv": reduced_conv,
    }
    current_route = "simple_request"

    async for update in graph.astream(graph_state, stream_mode="updates"):
        if "classification" in update:
            cl = update["classification"].get("route")
            current_route = cl or current_route
            yield emit("classification", {"value": cl})
            _log_event("classification", {
                "session_id": session_id,
                "route": cl,
                "prompt": prompt,
            })

        if "db_schema" in update:
            yield emit("status", {"message": "generando sql"})

        if "sql_query" in update:
            sql_query = update["sql_query"].get("sql_query", "")
            yield emit("sql_query", {"query": sql_query})

        if "query_results" in update:
            yield emit("status", {"message": "ejecutando sql"})
            result_str = update["query_results"].get("query_results", "")
            yield emit("query_results", {"results": result_str})

        if "finalize" in update:
            payload = update["finalize"].get("payload", payload)

        if "error_node" in update:
            payload = update["error_node"].get("payload", payload)

    yield emit("status", {"message": "generando respuesta"})

    if current_route == "malicious_request":
        response_text = MALICIOUS_SHORT_RESPONSE
        yield emit("model_token", {
            "delta": json.dumps({"delta": response_text})
        })
        conv_store.setdefault(session_id, []).append({
            "role": "assistant",
            "content": response_text,
        })
        yield emit("final", {})
        return


    response_text = ""
    stream_buffer = ""
    try:
        async for token in stream_from_ollama(payload, reduced_conv):
            response_text += token
            stream_buffer = (stream_buffer + token)[-500:]
            if _stream_contains_sensitive(stream_buffer):
                _log_event("stream_cut", {
                    "session_id": session_id,
                    "reason": "sensitive_term_match",
                })
                response_text += "\n[Respuesta bloqueada por seguridad]\n"
                yield emit("model_token", {
                    "delta": json.dumps({"delta": "\n[Respuesta bloqueada por seguridad]\n"})
                })
                break
            yield emit("model_token", {
                "delta": json.dumps({"delta": token})
            })
    except Exception:
        err = "\n[Error al contactar el modelo]\n"
        response_text += err
        yield emit("model_token", {
            "delta": json.dumps({"delta": err})
        })

    conv_store.setdefault(session_id, []).append({
        "role": "assistant",
        "content": response_text,
    })

    yield emit("final", {})


@app.post("/orchestrate")
async def orchestrate(request: Request):
    payload = await request.json()

    return StreamingResponse(
        orchestrated_stream(payload),
        media_type="text/event-stream"
    )

#get all convs

@app.get("/_debug/convs")
async def get_convs():
    return conv_store


@app.get("/_debug/ollama")
async def get_ollama_status():
    return await get_ollama_runtime_status()


@app.get("/_debug/graph")
async def get_orchestration_graph():
    _graph = graph.get_graph()
    return _graph.to_json(with_schemas=True)


@app.get("/_debug/graph.png")
async def get_orchestration_graph_png():
    _graph = graph.get_graph()
    img_bytes = _graph.draw_mermaid_png(
        curve_style=CurveStyle.LINEAR,
        node_colors=NodeStyles(first="#ffdfba", last="#baffc9", default="#fad7de"),
        wrap_label_n_words=9,
        output_file_path=None,
        draw_method=MermaidDrawMethod.API,
        background_color="white",
        padding=10,
    )
    return Response(content=img_bytes, media_type="image/png")

@app.get("/_debug/convs/clear")
async def clear_convs():
    conv_store.clear()
    return {"status": "convs cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
