#!/usr/bin/env python3
import json
import os
import glob
from typing import Dict, Any, List


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    failed = total - passed

    error_code_counts: Dict[int, int] = {}
    route_mismatch = 0
    leakage = 0
    for r in results:
        ec = int(r.get("error_code", 0))
        error_code_counts[ec] = error_code_counts.get(ec, 0) + 1
        for err in r.get("errors", []):
            if "Ruta esperada" in err:
                route_mismatch += 1
            if "Respuesta contiene datos sensibles" in err:
                leakage += 1

    variants: Dict[str, Dict[str, int]] = {}
    for r in results:
        vid = r.get("variant_id", "(sin-id)")
        if vid not in variants:
            variants[vid] = {"total": 0, "fail": 0}
        variants[vid]["total"] += 1
        if not r.get("passed"):
            variants[vid]["fail"] += 1

    worst_variants = sorted(
        variants.items(), key=lambda x: (-x[1]["fail"], x[0])
    )

    pass_rate = (passed / total) * 100 if total else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "error_code_counts": dict(sorted(error_code_counts.items())),
        "route_mismatch": route_mismatch,
        "leakage": leakage,
        "worst_variants": worst_variants,
    }


def _format_summary(name: str, model: str, summary: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"=== {name} ===")
    lines.append(f"Modelo: {model}")
    lines.append(
        f"Total: {summary['total']} | OK: {summary['passed']} | "
        f"Fallos: {summary['failed']} | "
        f"Tasa OK: {summary['pass_rate']:.2f}%"
    )
    lines.append(
        f"Ruta incorrecta: {summary['route_mismatch']} | "
        f"Fuga detectada: {summary['leakage']}"
    )
    lines.append(f"Error codes: {summary['error_code_counts']}")

    worst = summary["worst_variants"][:5]
    if worst:
        lines.append("Variantes más problemáticas (top 5):")
        for vid, stats in worst:
            lines.append(f"  - {vid}: {stats['fail']}/{stats['total']} fallos")

    return "\n".join(lines)


def _collect_inputs(results_dir: str, pattern: str) -> List[str]:
    candidates = glob.glob(os.path.join(results_dir, pattern))
    return sorted(candidates)


def main() -> None:
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    pattern = "safety_results_*.json"

    input_paths = _collect_inputs(results_dir, pattern)
    if not input_paths:
        raise SystemExit(f"No se encontraron resultados en {results_dir}")

    for path in input_paths:
        payload = _load_json(path)
        results = payload.get("results", [])
        if not results:
            print(f"[AVISO] Sin resultados en {path}")
            continue

        model = payload.get("model", os.path.basename(path))
        name = os.path.basename(path)
        summary = _summarize_results(results)

        print(_format_summary(name, model, summary))
        print()


if __name__ == "__main__":
    main()
