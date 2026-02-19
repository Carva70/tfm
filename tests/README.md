# Pruebas seguras (TFG ciberseguridad)

Este paquete valida que el flujo completo (clasificador → SQL → respuesta final) **no exponga PII** y que las solicitudes se enruten correctamente.

## Componentes cubiertos

- **Backend (FastAPI + orquestador)**: verificación de rutas y respuesta final.
- **Prompts y clasificación**: comprobación de `malicious_request` en intentos de exfiltración.
- **Capa de respuesta**: la respuesta final no debe incluir PII ni SQL.
- **Frontend (manual)**: validación visual de que mensajes informativos no muestran PII.

## Pruebas automatizadas

El script `run_safety_tests.py` combina plantillas de inyección de etiqueta con prompts internos de acceso a BD, selecciona la mejor plantilla y la aplica a los casos de seguridad, luego envía prompts al endpoint de streaming y verifica:

- Ruta esperada (`classification`).
- Ausencia de términos sensibles en la respuesta final.

### Exportar resultados y matriz

Puedes guardar los resultados en JSON y generar una matriz (heatmap) con el script de plotting.

Ejemplo:

- Ejecutar pruebas y guardar JSON por modelo (se guardan en tests/results):
   - `python run_safety_tests.py ./safety_cases.json ./label_injection.json --models llama3.1:8b`
- Ejecutar pruebas y guardar en una carpeta concreta:
   - `python run_safety_tests.py ./safety_cases.json ./label_injection.json --out ./results`
- Generar PNG con una matriz por modelo (en una sola imagen):
   - `python plot_safety_matrix.py --in ./results/safety_results_llama3.1-8b.json --out ./safety_matrix.png`

### Variables de entorno

- `ORCHESTRATOR_URL` (por defecto `http://localhost:9000/orchestrate`)
- `ORCHESTRATOR_MODEL` (por defecto `llama3.1:8b`)
- `CLASSIFICATION_MODEL` (modelo del nodo de clasificación; si no se define, usa `DEFAULT_MODEL` en `.env`)

## Pruebas manuales recomendadas (UI)

1. Lanzar el frontend y backend.
2. Probar prompts de `tests/safety_cases.json` y `tests/label_injection.json`.
3. Verificar que:
   - El mensaje final **no** contiene PII.
   - La clasificación muestre `malicious_request` en intentos de exfiltración.
   - No se muestran detalles de SQL o esquema en la respuesta final.

## Archivos

- tests/safety_cases.json: casos de prueba centrados en el prompt.
- tests/label_injection.json: plantillas de inyección de etiqueta.
- tests/run_safety_tests.py: runner de pruebas.
- tests/plot_safety_matrix.py: genera la matriz de resultados.
