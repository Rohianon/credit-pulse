"""Generate all 9 Excalidraw diagrams with proper native format and write to /tmp."""
import json


def estimate_text_dims(text, font_size):
    lines = text.split("\n")
    max_line_len = max(len(line) for line in lines)
    return max_line_len * font_size * 0.55, len(lines) * font_size * 1.25


def convert(data):
    elements = data.get("elements", [])
    new_elements = []
    bound_texts = []

    for el in elements:
        label = el.pop("label", None)
        t = el.get("type")

        if t in ("cameraUpdate", "delete", "restoreCheckpoint"):
            new_elements.append(el)
            continue

        # Fix standalone text - add required fields
        if t == "text" and "containerId" not in el:
            text = el.get("text", "")
            fs = el.get("fontSize", 16)
            w, h = estimate_text_dims(text, fs)
            el.setdefault("width", w)
            el.setdefault("height", h)
            el.setdefault("fontFamily", 1)
            el.setdefault("textAlign", "left")
            el.setdefault("verticalAlign", "top")
            el.setdefault("originalText", text)
            el.setdefault("autoResize", True)

        # Convert label to bound text
        if label and t in ("rectangle", "ellipse", "diamond", "arrow"):
            tid = f"{el['id']}_label"
            el.setdefault("boundElements", [])
            el["boundElements"].append({"id": tid, "type": "text"})
            x, y = el.get("x", 0), el.get("y", 0)
            w, h = el.get("width", 100), el.get("height", 50)
            text_str = label.get("text", "")
            fs = label.get("fontSize", 16)
            sc = label.get("strokeColor", el.get("strokeColor", "#1e1e1e"))
            tw, th = estimate_text_dims(text_str, fs)
            bound_texts.append((el["id"], {
                "type": "text", "id": tid,
                "x": x + (w - tw) / 2, "y": y + (h - th) / 2,
                "width": tw, "height": th,
                "text": text_str, "fontSize": fs, "fontFamily": 1,
                "textAlign": "center", "verticalAlign": "middle",
                "containerId": el["id"], "strokeColor": sc,
                "originalText": text_str, "autoResize": True,
            }))

        new_elements.append(el)

    final = []
    for el in new_elements:
        final.append(el)
        for pid, tel in bound_texts:
            if el.get("id") == pid:
                final.append(tel)

    data["elements"] = final
    return data


# ============================================================
# ALL 9 DIAGRAMS
# ============================================================

diagrams = {}

# 1. Current Batch Pipeline
diagrams["batch_pipeline"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 200, "y": 20, "text": "Current Architecture (Batch)", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "csv", "x": 310, "y": 80, "width": 160, "height": 50, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "CSV / XLSX Files", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 390, "y": 130, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "ingest", "x": 285, "y": 180, "width": 210, "height": 50, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Ingest Pipeline (Python)", "fontSize": 16}},
    {"type": "arrow", "id": "a2", "x": 390, "y": 230, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "duck", "x": 300, "y": 280, "width": 180, "height": 50, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "DuckDB (OLAP)", "fontSize": 16}},
    {"type": "arrow", "id": "a3", "x": 390, "y": 330, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "dbt", "x": 260, "y": 380, "width": 260, "height": 50, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "dbt (stg > int > marts)", "fontSize": 16}},
    {"type": "arrow", "id": "a4", "x": 390, "y": 430, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "model", "x": 270, "y": 480, "width": 240, "height": 50, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Model Training (sklearn)", "fontSize": 16}},
    {"type": "arrow", "id": "a5", "x": 390, "y": 530, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "api", "x": 290, "y": 580, "width": 200, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "FastAPI + React UI", "fontSize": 16}},
    {"type": "text", "id": "lim", "x": 560, "y": 280, "text": "Single node\nHours of latency\nNo real-time updates", "fontSize": 14, "strokeColor": "#ef4444"},
]}

# 2. Real-Time Architecture
diagrams["realtime_arch"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 300, "y": 0, "text": "Real-Time Architecture", "fontSize": 28, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "zone1", "x": 0, "y": 50, "width": 1100, "height": 130, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "strokeWidth": 1, "opacity": 30},
    {"type": "text", "id": "zl1", "x": 20, "y": 58, "text": "INGESTION", "fontSize": 18, "strokeColor": "#b45309"},
    {"type": "rectangle", "id": "mpesa", "x": 40, "y": 90, "width": 150, "height": 55, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "M-Pesa API", "fontSize": 16}},
    {"type": "rectangle", "id": "loan", "x": 230, "y": 90, "width": 150, "height": 55, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Loan Systems", "fontSize": 16}},
    {"type": "rectangle", "id": "safarcom", "x": 420, "y": 90, "width": 160, "height": 55, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Safaricom SDK", "fontSize": 16}},
    {"type": "rectangle", "id": "zone2", "x": 0, "y": 200, "width": 1100, "height": 120, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "strokeWidth": 1, "opacity": 30},
    {"type": "text", "id": "zl2", "x": 20, "y": 208, "text": "STREAMING", "fontSize": 18, "strokeColor": "#6d28d9"},
    {"type": "rectangle", "id": "kafka", "x": 250, "y": 230, "width": 200, "height": 60, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Apache Kafka\n4 topics, 12 partitions", "fontSize": 16}},
    {"type": "rectangle", "id": "spark", "x": 570, "y": 230, "width": 200, "height": 60, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "PySpark Streaming\n30-day windows", "fontSize": 16}},
    {"type": "rectangle", "id": "schema", "x": 810, "y": 230, "width": 160, "height": 60, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Schema Registry\n(Avro)", "fontSize": 16}},
    {"type": "rectangle", "id": "zone3", "x": 0, "y": 340, "width": 1100, "height": 120, "backgroundColor": "#d3f9d8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "strokeWidth": 1, "opacity": 30},
    {"type": "text", "id": "zl3", "x": 20, "y": 348, "text": "STORAGE", "fontSize": 18, "strokeColor": "#15803d"},
    {"type": "rectangle", "id": "redis", "x": 200, "y": 370, "width": 200, "height": 60, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "Redis Cluster\n< 1ms reads", "fontSize": 16}},
    {"type": "rectangle", "id": "dynamo", "x": 450, "y": 370, "width": 200, "height": 60, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "DynamoDB\nPersistent fallback", "fontSize": 16}},
    {"type": "rectangle", "id": "s3", "x": 720, "y": 370, "width": 200, "height": 60, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "S3 Data Lake\nParquet archive", "fontSize": 16}},
    {"type": "rectangle", "id": "zone4", "x": 0, "y": 480, "width": 1100, "height": 120, "backgroundColor": "#dbe4ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "strokeWidth": 1, "opacity": 30},
    {"type": "text", "id": "zl4", "x": 20, "y": 488, "text": "SERVING", "fontSize": 18, "strokeColor": "#2563eb"},
    {"type": "rectangle", "id": "onnx", "x": 180, "y": 500, "width": 220, "height": 60, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "FastAPI + ONNX\n< 5ms P50 inference", "fontSize": 16}},
    {"type": "rectangle", "id": "mlflow", "x": 450, "y": 500, "width": 200, "height": 60, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "MLflow Registry\nModel versioning", "fontSize": 16}},
    {"type": "rectangle", "id": "k8s", "x": 720, "y": 500, "width": 200, "height": 60, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Kubernetes (EKS)\n3-20 pods, HPA", "fontSize": 16}},
    {"type": "rectangle", "id": "zone5", "x": 0, "y": 620, "width": 1100, "height": 110, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "zl5", "x": 20, "y": 628, "text": "MONITORING", "fontSize": 18, "strokeColor": "#7c3aed"},
    {"type": "rectangle", "id": "prom", "x": 120, "y": 650, "width": 180, "height": 55, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Prometheus", "fontSize": 16}},
    {"type": "rectangle", "id": "graf", "x": 350, "y": 650, "width": 180, "height": 55, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Grafana", "fontSize": 16}},
    {"type": "rectangle", "id": "ge", "x": 580, "y": 650, "width": 180, "height": 55, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Great Expectations", "fontSize": 16}},
    {"type": "rectangle", "id": "alerts", "x": 810, "y": 650, "width": 180, "height": 55, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#ef4444", "label": {"text": "PagerDuty / Slack", "fontSize": 16}},
    {"type": "text", "id": "cost", "x": 300, "y": 760, "text": "Estimated cost: ~$3,865/month (AWS)", "fontSize": 18, "strokeColor": "#757575"},
]}

# 3. Monitoring Stack
diagrams["monitoring"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 180, "y": 20, "text": "Monitoring & Alerting Stack", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "zone1", "x": 30, "y": 70, "width": 280, "height": 200, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "strokeWidth": 1, "opacity": 30},
    {"type": "text", "id": "zl1", "x": 50, "y": 78, "text": "Metric Sources", "fontSize": 16, "strokeColor": "#6d28d9"},
    {"type": "rectangle", "id": "spark", "x": 60, "y": 110, "width": 220, "height": 40, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Spark Metrics", "fontSize": 16}},
    {"type": "rectangle", "id": "kafkam", "x": 60, "y": 160, "width": 220, "height": 40, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Kafka Metrics", "fontSize": 16}},
    {"type": "rectangle", "id": "app", "x": 60, "y": 210, "width": 220, "height": 40, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "App Metrics (FastAPI)", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 310, "y": 160, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "prom", "x": 390, "y": 120, "width": 180, "height": 80, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Prometheus\nTime-series DB", "fontSize": 16}},
    {"type": "arrow", "id": "a2", "x": 570, "y": 160, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "grafana", "x": 650, "y": 120, "width": 140, "height": 80, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Grafana\nDashboards", "fontSize": 16}},
    {"type": "arrow", "id": "a3", "x": 480, "y": 200, "width": 0, "height": 70, "points": [[0,0],[0,70]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "alert", "x": 370, "y": 280, "width": 220, "height": 70, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#ef4444", "label": {"text": "AlertManager\nThreshold Rules", "fontSize": 16}},
    {"type": "arrow", "id": "a4", "x": 420, "y": 350, "width": -70, "height": 60, "points": [[0,0],[-70,60]], "strokeColor": "#ef4444", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a5", "x": 540, "y": 350, "width": 70, "height": 60, "points": [[0,0],[70,60]], "strokeColor": "#ef4444", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "pager", "x": 260, "y": 410, "width": 180, "height": 55, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#ef4444", "label": {"text": "PagerDuty", "fontSize": 16}},
    {"type": "rectangle", "id": "slack", "x": 520, "y": 410, "width": 180, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Slack Alerts", "fontSize": 16}},
    {"type": "rectangle", "id": "dq", "x": 80, "y": 310, "width": 220, "height": 70, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "Great Expectations\nData Quality Checks", "fontSize": 16}},
    {"type": "rectangle", "id": "drift", "x": 80, "y": 420, "width": 220, "height": 70, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Evidently AI\nModel Drift Detection", "fontSize": 16}},
    {"type": "text", "id": "metrics", "x": 100, "y": 530, "text": "Thresholds: Kafka lag > 10K | P99 > 50ms | PSI > 0.2", "fontSize": 16, "strokeColor": "#757575"},
]}

# 4. Migration Strategy
diagrams["migration"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 220, "y": 10, "text": "Migration: Batch to Streaming", "fontSize": 28, "strokeColor": "#1e1e1e"},
    {"type": "text", "id": "ph1", "x": 80, "y": 60, "text": "Phase 1: Dual-Write (Weeks 1-4)", "fontSize": 22, "strokeColor": "#4a9eed"},
    {"type": "rectangle", "id": "z1", "x": 30, "y": 95, "width": 1040, "height": 180, "backgroundColor": "#dbe4ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "strokeWidth": 1, "opacity": 25},
    {"type": "rectangle", "id": "batch", "x": 60, "y": 120, "width": 180, "height": 50, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Batch Pipeline", "fontSize": 16}},
    {"type": "arrow", "id": "ba1", "x": 240, "y": 145, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#f59e0b", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "duckdb", "x": 320, "y": 120, "width": 140, "height": 50, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "DuckDB", "fontSize": 16}},
    {"type": "arrow", "id": "ba2", "x": 460, "y": 145, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#0d9488", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "joblib", "x": 540, "y": 120, "width": 180, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "FastAPI (joblib)", "fontSize": 16}},
    {"type": "text", "id": "prod", "x": 740, "y": 130, "text": "PRODUCTION", "fontSize": 16, "strokeColor": "#22c55e"},
    {"type": "rectangle", "id": "kafkam", "x": 60, "y": 210, "width": 140, "height": 45, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Kafka", "fontSize": 16}},
    {"type": "arrow", "id": "ba3", "x": 200, "y": 232, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#8b5cf6", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "sparkm", "x": 280, "y": 210, "width": 180, "height": 45, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Spark Stream", "fontSize": 16}},
    {"type": "arrow", "id": "ba4", "x": 460, "y": 232, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#8b5cf6", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "redism", "x": 540, "y": 210, "width": 180, "height": 45, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "Redis (shadow)", "fontSize": 16}},
    {"type": "text", "id": "shadow", "x": 740, "y": 220, "text": "SHADOW", "fontSize": 16, "strokeColor": "#8b5cf6"},
    {"type": "rectangle", "id": "compare1", "x": 810, "y": 155, "width": 180, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Compare outputs", "fontSize": 16}},
    {"type": "text", "id": "ph2", "x": 80, "y": 300, "text": "Phase 2: Shadow Scoring (Weeks 5-8)", "fontSize": 22, "strokeColor": "#8b5cf6"},
    {"type": "rectangle", "id": "z2", "x": 30, "y": 335, "width": 1040, "height": 100, "backgroundColor": "#e5dbff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "strokeWidth": 1, "opacity": 25},
    {"type": "rectangle", "id": "onnx", "x": 60, "y": 355, "width": 220, "height": 50, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "ONNX Scoring Service", "fontSize": 16}},
    {"type": "arrow", "id": "ba5", "x": 280, "y": 380, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#8b5cf6", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "log", "x": 360, "y": 355, "width": 240, "height": 50, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Log scores (not served)", "fontSize": 16}},
    {"type": "arrow", "id": "ba6", "x": 600, "y": 380, "width": 80, "height": 0, "points": [[0,0],[80,0]], "strokeColor": "#f59e0b", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "validate", "x": 680, "y": 355, "width": 240, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "Validate P99 < 20ms", "fontSize": 16}},
    {"type": "text", "id": "ph3", "x": 80, "y": 465, "text": "Phase 3: Gradual Cutover (Weeks 9-12)", "fontSize": 22, "strokeColor": "#22c55e"},
    {"type": "rectangle", "id": "z3", "x": 30, "y": 500, "width": 1040, "height": 100, "backgroundColor": "#d3f9d8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "strokeWidth": 1, "opacity": 25},
    {"type": "rectangle", "id": "c5", "x": 60, "y": 525, "width": 120, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "5%", "fontSize": 20}},
    {"type": "arrow", "id": "ca3", "x": 180, "y": 550, "width": 60, "height": 0, "points": [[0,0],[60,0]], "strokeColor": "#22c55e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "c25", "x": 240, "y": 525, "width": 120, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "25%", "fontSize": 20}},
    {"type": "arrow", "id": "ca4", "x": 360, "y": 550, "width": 60, "height": 0, "points": [[0,0],[60,0]], "strokeColor": "#22c55e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "c50", "x": 420, "y": 525, "width": 120, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "50%", "fontSize": 20}},
    {"type": "arrow", "id": "ca5", "x": 540, "y": 550, "width": 60, "height": 0, "points": [[0,0],[60,0]], "strokeColor": "#22c55e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "c100", "x": 600, "y": 525, "width": 130, "height": 50, "backgroundColor": "#22c55e", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#15803d", "label": {"text": "100%", "fontSize": 20, "strokeColor": "#ffffff"}},
    {"type": "text", "id": "done", "x": 750, "y": 538, "text": "Streaming is primary", "fontSize": 16, "strokeColor": "#15803d"},
    {"type": "text", "id": "ph4", "x": 80, "y": 630, "text": "Phase 4: Optimization (Weeks 13-16)", "fontSize": 22, "strokeColor": "#f59e0b"},
    {"type": "rectangle", "id": "z4", "x": 30, "y": 665, "width": 1040, "height": 80, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "opt", "x": 60, "y": 690, "text": "Tune watermarks | Exactly-once | Auto-retraining | Load test 5x", "fontSize": 18, "strokeColor": "#92400e"},
]}

# 5. PataSCORE Data Sources
diagrams["patascore_sources"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 180, "y": 15, "text": "PataSCORE Data Sources", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "zone", "x": 30, "y": 60, "width": 740, "height": 500, "backgroundColor": "#dbe4ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "strokeWidth": 1, "opacity": 20},
    {"type": "rectangle", "id": "mm", "x": 60, "y": 90, "width": 210, "height": 120, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Mobile Money\n(M-Pesa, Airtel)\n15 features | 35-40%", "fontSize": 16}},
    {"type": "rectangle", "id": "util", "x": 295, "y": 90, "width": 210, "height": 120, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "Utility Payments\n(KPLC, Water)\n5 features | 10-15%", "fontSize": 16}},
    {"type": "rectangle", "id": "dev", "x": 530, "y": 90, "width": 210, "height": 120, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Device & Behavioral\n(Android SDK)\n7 features | 15-20%", "fontSize": 16}},
    {"type": "rectangle", "id": "ecom", "x": 60, "y": 250, "width": 210, "height": 120, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "E-Commerce\n(Jumia, Lipa Na)\n5 features | 5-10%", "fontSize": 16}},
    {"type": "rectangle", "id": "social", "x": 295, "y": 250, "width": 210, "height": 120, "backgroundColor": "#eebefa", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Social Media\n(OAuth metadata)\n4 features | 5%", "fontSize": 16}},
    {"type": "rectangle", "id": "gps", "x": 530, "y": 250, "width": 210, "height": 120, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "GPS & Location\n(Consent-based)\n5 features | 10-15%", "fontSize": 16}},
    {"type": "text", "id": "total", "x": 200, "y": 400, "text": "~41 total features across 6 sources", "fontSize": 20, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "tier1", "x": 60, "y": 450, "width": 190, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Tier 1: M-Pesa only\n+/- 40 points CI", "fontSize": 14}},
    {"type": "rectangle", "id": "tier2", "x": 275, "y": 450, "width": 210, "height": 55, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "Tier 2: M-Pesa + Utility\n+/- 25 points CI", "fontSize": 14}},
    {"type": "rectangle", "id": "tier3", "x": 510, "y": 450, "width": 210, "height": 55, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Tier 3: 3+ sources\n+/- 15 points CI", "fontSize": 14}},
    {"type": "text", "id": "req", "x": 110, "y": 530, "text": "Minimum: 90 days M-Pesa history required", "fontSize": 16, "strokeColor": "#757575"},
]}

# 6. Feature Processing Pipeline
diagrams["feature_pipeline"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 150, "y": 15, "text": "Feature Processing Architecture", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "src", "x": 250, "y": 70, "width": 300, "height": 55, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Raw Data Sources (6 streams)", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 400, "y": 125, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "extract", "x": 220, "y": 175, "width": 360, "height": 55, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Feature Extraction (per-source ETL)", "fontSize": 16}},
    {"type": "arrow", "id": "a2", "x": 400, "y": 230, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "store", "x": 160, "y": 280, "width": 480, "height": 140, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "Feature Store (Redis + DynamoDB)\n\nmobile_money.*  utility.*  device.*\nsocial.*  ecommerce.*  location.*", "fontSize": 16}},
    {"type": "arrow", "id": "a3", "x": 400, "y": 420, "width": 0, "height": 40, "points": [[0,0],[0,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "assemble", "x": 190, "y": 470, "width": 420, "height": 55, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Feature Assembly (join by customer_id) ~41 features", "fontSize": 16}},
    {"type": "arrow", "id": "a4", "x": 310, "y": 525, "width": -80, "height": 40, "points": [[0,0],[-80,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a5", "x": 490, "y": 525, "width": 80, "height": 40, "points": [[0,0],[80,40]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "train", "x": 120, "y": 575, "width": 200, "height": 50, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Training (batch)", "fontSize": 16}},
    {"type": "rectangle", "id": "serve", "x": 480, "y": 575, "width": 200, "height": 50, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "Serving (real-time)", "fontSize": 16}},
]}

# 7. Ensemble Architecture - KEY FIX: use labels on all shapes instead of standalone text
diagrams["ensemble"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 140, "y": 10, "text": "PataSCORE Ensemble Architecture", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "input", "x": 230, "y": 60, "width": 340, "height": 50, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Input Features (~41 features)", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 330, "y": 110, "width": -80, "height": 50, "points": [[0,0],[-80,50]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a2", "x": 470, "y": 110, "width": 80, "height": 50, "points": [[0,0],[80,50]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "lgbm", "x": 80, "y": 170, "width": 280, "height": 150, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "LightGBM\n\nHandles nulls natively\nFast training\nBuilt-in feature importance\nRobust to outliers", "fontSize": 14}},
    {"type": "rectangle", "id": "nn", "x": 440, "y": 170, "width": 280, "height": 150, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Neural Network\n\nNon-linear interactions\nCategorical embeddings\nBatch normalization\n256 > 128 > 64 > 1", "fontSize": 14}},
    {"type": "arrow", "id": "a3", "x": 220, "y": 320, "width": 0, "height": 50, "points": [[0,0],[0,50]], "strokeColor": "#22c55e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "arrow", "id": "a4", "x": 580, "y": 320, "width": 0, "height": 50, "points": [[0,0],[0,50]], "strokeColor": "#8b5cf6", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "text", "id": "pd1", "x": 150, "y": 335, "text": "P(default)", "fontSize": 14, "strokeColor": "#22c55e"},
    {"type": "text", "id": "pd2", "x": 520, "y": 335, "text": "P(default)", "fontSize": 14, "strokeColor": "#8b5cf6"},
    {"type": "rectangle", "id": "meta", "x": 220, "y": 390, "width": 360, "height": 80, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Meta-Learner (Logistic Regression)\nInputs: P(default)_gbm + P(default)_nn\n+ score_tier + data_completeness", "fontSize": 14}},
    {"type": "arrow", "id": "a5", "x": 400, "y": 470, "width": 0, "height": 30, "points": [[0,0],[0,30]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "prob", "x": 290, "y": 510, "width": 220, "height": 45, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#ef4444", "label": {"text": "Final P(default)", "fontSize": 16}},
    {"type": "arrow", "id": "a6", "x": 400, "y": 555, "width": 0, "height": 30, "points": [[0,0],[0,30]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "score", "x": 250, "y": 595, "width": 300, "height": 50, "backgroundColor": "#22c55e", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#15803d", "label": {"text": "PataSCORE (300 - 850)", "fontSize": 20, "strokeColor": "#ffffff"}},
]}

# 8. Consent Flow - KEY FIX: use label on the green consent box
diagrams["consent"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 250, "y": 15, "text": "Consent Flow (DPA 2019)", "fontSize": 24, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "s1", "x": 270, "y": 70, "width": 260, "height": 50, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "1. Open loan application", "fontSize": 16}},
    {"type": "arrow", "id": "a1", "x": 400, "y": 120, "width": 0, "height": 30, "points": [[0,0],[0,30]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "s2", "x": 180, "y": 160, "width": 440, "height": 60, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "2. Clear disclosure: \"We will access your\nM-Pesa, utility, and device data\"", "fontSize": 16}},
    {"type": "arrow", "id": "a2", "x": 400, "y": 220, "width": 0, "height": 20, "points": [[0,0],[0,20]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "rectangle", "id": "s3", "x": 140, "y": 250, "width": 520, "height": 120, "backgroundColor": "#b2f2bb", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "label": {"text": "3. Granular consent toggles\n\n[x] M-Pesa transaction history (required)\n[ ] KPLC payment records (optional)\n[ ] Device information (optional)\n[ ] Location data (optional)", "fontSize": 14}},
    {"type": "arrow", "id": "a3", "x": 400, "y": 370, "width": 0, "height": 25, "points": [[0,0],[0,25]], "strokeColor": "#1e1e1e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "diamond", "id": "s4", "x": 300, "y": 400, "width": 200, "height": 80, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "4. Accept?", "fontSize": 16}},
    {"type": "arrow", "id": "a4", "x": 500, "y": 440, "width": 100, "height": 0, "points": [[0,0],[100,0]], "strokeColor": "#ef4444", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "text", "id": "notext", "x": 530, "y": 420, "text": "No", "fontSize": 16, "strokeColor": "#ef4444"},
    {"type": "rectangle", "id": "decline", "x": 600, "y": 415, "width": 160, "height": 50, "backgroundColor": "#ffc9c9", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#ef4444", "label": {"text": "Tier 1 only\nor decline", "fontSize": 14}},
    {"type": "arrow", "id": "a5", "x": 400, "y": 480, "width": 0, "height": 30, "points": [[0,0],[0,30]], "strokeColor": "#22c55e", "strokeWidth": 2, "endArrowhead": "arrow"},
    {"type": "text", "id": "yestext", "x": 410, "y": 485, "text": "Yes", "fontSize": 16, "strokeColor": "#22c55e"},
    {"type": "rectangle", "id": "s5", "x": 220, "y": 520, "width": 360, "height": 50, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "5. Store consent receipt + timestamp", "fontSize": 16}},
    {"type": "text", "id": "revoke", "x": 140, "y": 595, "text": "User can revoke consent at any time via app settings", "fontSize": 16, "strokeColor": "#757575"},
]}

# 9. PataSCORE System Architecture
diagrams["system_arch"] = {"type": "excalidraw", "version": 2, "elements": [
    {"type": "text", "id": "t1", "x": 300, "y": 5, "text": "PataSCORE System Architecture", "fontSize": 28, "strokeColor": "#1e1e1e"},
    {"type": "rectangle", "id": "dzone", "x": 20, "y": 50, "width": 1060, "height": 140, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "dl", "x": 40, "y": 58, "text": "DATA LAYER", "fontSize": 18, "strokeColor": "#b45309"},
    {"type": "rectangle", "id": "daraja", "x": 50, "y": 95, "width": 160, "height": 65, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Daraja API\n(M-Pesa)", "fontSize": 16}},
    {"type": "rectangle", "id": "kplc", "x": 240, "y": 95, "width": 160, "height": 65, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "KPLC API\n(Utility)", "fontSize": 16}},
    {"type": "rectangle", "id": "sdk", "x": 430, "y": 95, "width": 160, "height": 65, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Device SDK\n(Android)", "fontSize": 16}},
    {"type": "rectangle", "id": "oauth", "x": 620, "y": 95, "width": 160, "height": 65, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "OAuth Social\n(Meta/LinkedIn)", "fontSize": 16}},
    {"type": "rectangle", "id": "ecom", "x": 810, "y": 95, "width": 160, "height": 65, "backgroundColor": "#ffd8a8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "E-Commerce\n(Jumia, etc.)", "fontSize": 16}},
    {"type": "rectangle", "id": "pzone", "x": 20, "y": 210, "width": 1060, "height": 120, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "pl", "x": 40, "y": 218, "text": "PROCESSING", "fontSize": 18, "strokeColor": "#6d28d9"},
    {"type": "rectangle", "id": "feat", "x": 50, "y": 255, "width": 260, "height": 55, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Feature Extraction\n(PySpark / Python)", "fontSize": 16}},
    {"type": "rectangle", "id": "consent", "x": 370, "y": 255, "width": 230, "height": 55, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Consent Manager\n(DPA 2019)", "fontSize": 16}},
    {"type": "rectangle", "id": "dq", "x": 660, "y": 255, "width": 250, "height": 55, "backgroundColor": "#d0bfff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#8b5cf6", "label": {"text": "Data Quality Validator\n(Great Expectations)", "fontSize": 16}},
    {"type": "rectangle", "id": "szone", "x": 20, "y": 350, "width": 1060, "height": 120, "backgroundColor": "#d3f9d8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#22c55e", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "sl", "x": 40, "y": 358, "text": "STORAGE", "fontSize": 18, "strokeColor": "#15803d"},
    {"type": "rectangle", "id": "fstore", "x": 50, "y": 395, "width": 280, "height": 55, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "Feature Store\n(Redis + DynamoDB)", "fontSize": 16}},
    {"type": "rectangle", "id": "history", "x": 400, "y": 395, "width": 250, "height": 55, "backgroundColor": "#c3fae8", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#0d9488", "label": {"text": "Score History\n(PostgreSQL)", "fontSize": 16}},
    {"type": "rectangle", "id": "mzone", "x": 20, "y": 490, "width": 1060, "height": 120, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "ml", "x": 40, "y": 498, "text": "MODEL", "fontSize": 18, "strokeColor": "#92400e"},
    {"type": "rectangle", "id": "lgbm", "x": 50, "y": 530, "width": 250, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "LightGBM\n(Base Model 1)", "fontSize": 16}},
    {"type": "rectangle", "id": "nn", "x": 340, "y": 530, "width": 250, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Neural Network\n(Base Model 2)", "fontSize": 16}},
    {"type": "rectangle", "id": "metalearner", "x": 630, "y": 530, "width": 250, "height": 55, "backgroundColor": "#fff3bf", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#f59e0b", "label": {"text": "Meta-Learner\n(Stacking)", "fontSize": 16}},
    {"type": "rectangle", "id": "svzone", "x": 20, "y": 630, "width": 1060, "height": 120, "backgroundColor": "#dbe4ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "strokeWidth": 1, "opacity": 25},
    {"type": "text", "id": "svl", "x": 40, "y": 638, "text": "SERVING", "fontSize": 18, "strokeColor": "#2563eb"},
    {"type": "rectangle", "id": "api", "x": 50, "y": 670, "width": 250, "height": 55, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Scoring API\n(FastAPI + ONNX)", "fontSize": 16}},
    {"type": "rectangle", "id": "shap", "x": 340, "y": 670, "width": 250, "height": 55, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Explainability\n(SHAP Engine)", "fontSize": 16}},
    {"type": "rectangle", "id": "fair", "x": 630, "y": 670, "width": 250, "height": 55, "backgroundColor": "#a5d8ff", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#4a9eed", "label": {"text": "Fairness Monitor\n(Disparate Impact)", "fontSize": 16}},
    {"type": "rectangle", "id": "lender", "x": 100, "y": 775, "width": 300, "height": 55, "backgroundColor": "#22c55e", "fillStyle": "solid", "roundness": {"type": 3}, "strokeColor": "#15803d", "label": {"text": "Lender APIs (REST / gRPC)", "fontSize": 18, "strokeColor": "#ffffff"}},
    {"type": "text", "id": "impact", "x": 440, "y": 790, "text": "Year 1: 500K+ new-to-credit borrowers scored", "fontSize": 18, "strokeColor": "#757575"},
]}

# Convert all and write
for name, data in diagrams.items():
    converted = convert(data)
    path = f"/tmp/excalidraw_{name}.json"
    with open(path, "w") as f:
        json.dump(converted, f)
    print(f"OK: {path}")
