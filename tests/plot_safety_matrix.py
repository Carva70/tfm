#!/usr/bin/env python3
import argparse
import json
import os
from typing import Dict, Any, List

import matplotlib.pyplot as plt
import numpy as np


def _load_results(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _build_matrix(results: List[Dict[str, Any]]):
    case_ids = sorted({r["case_id"] for r in results})
    variant_ids = sorted({r["variant_id"] for r in results})

    case_index = {cid: i for i, cid in enumerate(case_ids)}
    variant_index = {vid: j for j, vid in enumerate(variant_ids)}

    matrix = np.full((len(case_ids), len(variant_ids)), np.nan)
    for r in results:
        i = case_index[r["case_id"]]
        j = variant_index[r["variant_id"]]
        if "error_code" in r:
            matrix[i, j] = float(r.get("error_code", 0))
        else:
            matrix[i, j] = 0.0 if r.get("passed") else 1.0

    return case_ids, variant_ids, matrix


def main():
    parser = argparse.ArgumentParser(description="Matriz de resultados de pruebas de seguridad.")
    parser.add_argument(
        "--in",
        dest="input_paths",
        action="append",
        required=True,
        help="JSON generado por run_safety_tests.py (puede repetirse).",
    )
    parser.add_argument("--out", dest="output_path", help="Ruta para guardar PNG")
    parser.add_argument("--show", action="store_true", help="Mostrar ventana interactiva")
    args = parser.parse_args()

    input_paths = []
    for raw in args.input_paths:
        if "," in raw:
            input_paths.extend([p.strip() for p in raw.split(",") if p.strip()])
        else:
            input_paths.append(raw)

    payloads = []
    for path in input_paths:
        payload = _load_results(path)
        results = payload.get("results", [])
        if not results:
            raise SystemExit(f"No hay resultados en el JSON: {path}")
        payloads.append((path, payload, results))

    matrices = []
    max_cases = 0
    max_variants = 0
    for path, payload, results in payloads:
        case_ids, variant_ids, matrix = _build_matrix(results)
        max_cases = max(max_cases, len(case_ids))
        max_variants = max(max_variants, len(variant_ids))
        matrices.append((path, payload, case_ids, variant_ids, matrix))

    fig_width = max(5, min(12, max_variants * 0.7)) * len(matrices)
    fig_height = max(5, max_cases * 0.5)

    fig, axes = plt.subplots(
        1,
        len(matrices),
        figsize=(fig_width, fig_height),
        squeeze=False,
        constrained_layout=True,
    )
    axes = axes[0]

    cmap = plt.cm.get_cmap("RdYlGn_r")
    images = []

    for ax, (path, payload, case_ids, variant_ids, matrix) in zip(axes, matrices):
        im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2)
        images.append(im)

        ax.set_xticks(range(len(variant_ids)))
        ax.set_yticks(range(len(case_ids)))
        ax.set_xticklabels(variant_ids, rotation=45, ha="right")
        ax.set_yticklabels(case_ids)

        title = payload.get("model") or os.path.basename(path)
        ax.set_title(title)
        ax.set_xlabel("Variantes")
        ax.set_ylabel("Casos")

    for ax, im in zip(axes, images):
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle("Matriz de resultados (0=OK, 1=Error, 2=Crítico)")

    if args.output_path:
        fig.savefig(args.output_path, dpi=150)

    if args.show or not args.output_path:
        plt.show()


if __name__ == "__main__":
    main()
