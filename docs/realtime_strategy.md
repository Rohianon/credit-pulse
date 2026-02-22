# Real-Time Pipeline Strategy for Credit Pulse

## Task 5: Scaling to Real-Time Processing of 1M+ Transactions/Day

---

## 1. Current Architecture (Batch Processing)

Credit Pulse currently operates as a **batch-oriented pipeline** built on lightweight, local-first tooling:

[![Current Batch Architecture](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=0mxcnbIzAXt92AXHJ0F_R,0UahJCa_tLQgyEuLpmwtkA)

<img width="1068" height="1260" alt="image" src="https://github.com/user-attachments/assets/e5efca3d-5655-4dbc-9a90-593a0f9f2957" />


> **[Open interactive diagram](https://excalidraw.com/#json=0mxcnbIzAXt92AXHJ0F_R,0UahJCa_tLQgyEuLpmwtkA)** — CSV/XLSX Files → Ingest Pipeline → DuckDB → dbt Transformations → Model Training → FastAPI + React UI

**Current stack summary:**

| Component          | Technology               | Role                                    |
|--------------------|--------------------------|-----------------------------------------|
| Ingestion          | Python scripts           | Load CSV/XLSX into DuckDB tables        |
| Storage            | DuckDB                   | Embedded OLAP for analytical queries    |
| Transformation     | dbt-duckdb               | SQL-based feature engineering            |
| Feature columns    | 22 engineered features   | Transaction, balance, and category ratios|
| Model training     | XGBoost, Random Forest, Logistic Regression | 5-fold CV, best model selection |
| Model serving      | FastAPI + joblib          | Synchronous inference via REST           |
| Orchestration      | Makefile (Prefect-ready) | Sequential: ingest -> dbt -> train       |

**Limitations at scale:**

- DuckDB is single-node and embedded; cannot horizontally scale for concurrent writes
- Batch ingestion from flat files introduces hours of latency
- dbt transformations must re-process entire tables on each run
- Model retraining requires full pipeline re-execution
- joblib model loading on each request adds latency
- No real-time feature updates -- features go stale between batch runs

---

## 2. Proposed Real-Time Architecture

### 2.1 Architecture Overview

[![Real-Time Architecture](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=QoMucRy4IeGmNfZY8TnMj,oH1ZqS7JEOVm_9tgPlcFYg)

> **[Open interactive diagram](https://excalidraw.com/#json=QoMucRy4IeGmNfZY8TnMj,oH1ZqS7JEOVm_9tgPlcFYg)** — 5-layer architecture: Ingestion (M-Pesa API, Loan Systems, Safaricom SDK) → Streaming (Kafka, PySpark, Schema Registry) → Storage (Redis, DynamoDB, S3) → Serving (FastAPI + ONNX, MLflow, Kubernetes) → Monitoring (Prometheus, Grafana, Great Expectations, PagerDuty)

### 2.2 Component Breakdown

The real-time architecture is organized into five layers: **Ingestion**, **Stream Processing**, **Feature Storage**, **Model Serving**, and **Monitoring**.

---

## 3. Event-Driven Ingestion with Apache Kafka

### 3.1 Kafka Topic Design

```
Kafka Topics:
-------------------------------------------------
mpesa.transactions.raw     -- Raw M-Pesa events from Daraja API / webhooks
loan.events.raw            -- Loan origination, repayment, default events
features.computed          -- Computed feature vectors per customer
risk.scores.updates        -- Real-time score updates for downstream consumers
data.quality.alerts        -- DQ failures and anomaly detections
```

**Topic configuration for 1M+ transactions/day:**

```yaml
# ~12 transactions/second average, ~50/s peak
mpesa.transactions.raw:
  partitions: 12             # Partition by customer_id hash
  replication_factor: 3      # Durability across brokers
  retention.ms: 604800000    # 7-day retention for replay
  cleanup.policy: delete
  compression.type: lz4      # Fast compression for throughput

features.computed:
  partitions: 12
  replication_factor: 3
  retention.ms: 172800000    # 2-day retention
  cleanup.policy: compact    # Keep latest per customer_id key
```

### 3.2 Event Schema (Avro)

```json
{
  "type": "record",
  "name": "MpesaTransaction",
  "namespace": "com.creditpulse.events",
  "fields": [
    {"name": "event_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "transaction_id", "type": "string"},
    {"name": "transaction_type", "type": "string"},
    {"name": "received_amount", "type": "double"},
    {"name": "sent_amount", "type": "double"},
    {"name": "balance", "type": "double"},
    {"name": "transaction_at", "type": {"type": "long", "logicalType": "timestamp-millis"}},
    {"name": "tx_category", "type": "string"},
    {"name": "ingested_at", "type": {"type": "long", "logicalType": "timestamp-millis"}}
  ]
}
```

### 3.3 Ingestion Connectors

```python
# Kafka producer for M-Pesa Daraja API webhook handler
from confluent_kafka import Producer
from confluent_kafka.schema_registry.avro import AvroSerializer
import json

class MpesaEventProducer:
    def __init__(self, bootstrap_servers: str, schema_registry_url: str):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
            'linger.ms': 50,          # Micro-batch for throughput
            'batch.size': 65536,       # 64KB batches
            'compression.type': 'lz4',
            'acks': 'all',             # Full durability
        })
        # Schema registry integration omitted for brevity

    def publish_transaction(self, txn: dict):
        self.producer.produce(
            topic='mpesa.transactions.raw',
            key=txn['customer_id'].encode('utf-8'),
            value=json.dumps(txn).encode('utf-8'),
            callback=self._delivery_report,
        )

    def _delivery_report(self, err, msg):
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            logger.debug(f"Delivered to {msg.topic()}[{msg.partition()}]")
```

---

## 4. Stream Processing with PySpark Structured Streaming

### 4.1 Real-Time Feature Computation

The current dbt models compute 22 features in batch SQL. In the streaming architecture, PySpark Structured Streaming replicates this logic with **stateful windowed aggregations**.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

spark = SparkSession.builder \
    .appName("CreditPulse-FeatureStream") \
    .config("spark.sql.shuffle.partitions", 12) \
    .config("spark.streaming.kafka.maxRatePerPartition", 1000) \
    .getOrCreate()

# Read from Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "mpesa.transactions.raw") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parse and deserialize
txn_schema = StructType([
    StructField("customer_id", StringType()),
    StructField("transaction_id", StringType()),
    StructField("transaction_type", StringType()),
    StructField("received_amount", DoubleType()),
    StructField("sent_amount", DoubleType()),
    StructField("balance", DoubleType()),
    StructField("transaction_at", TimestampType()),
    StructField("tx_category", StringType()),
])

transactions = raw_stream \
    .select(F.from_json(F.col("value").cast("string"), txn_schema).alias("data")) \
    .select("data.*") \
    .withWatermark("transaction_at", "1 hour")

# Rolling 30-day window features (mirrors int_transaction_features.sql)
customer_features = transactions \
    .groupBy(
        F.col("customer_id"),
        F.window("transaction_at", "30 days", "1 day")
    ) \
    .agg(
        # Volume metrics
        F.count("*").alias("transaction_count"),
        F.countDistinct(F.to_date("transaction_at")).alias("active_days"),

        # Flow metrics
        F.sum("received_amount").alias("total_inflows"),
        F.sum("sent_amount").alias("total_outflows"),

        # Balance metrics
        F.avg("balance").alias("avg_balance"),
        F.min("balance").alias("min_balance"),
        F.max("balance").alias("max_balance"),
        F.stddev("balance").alias("balance_volatility"),

        # Received amount stats
        F.avg(F.when(F.col("received_amount") > 0, F.col("received_amount")))
            .alias("avg_received_amount"),
        F.max("received_amount").alias("max_received_amount"),

        # Spending consistency
        F.stddev("sent_amount").alias("spending_consistency"),

        # Category ratios (betting, utility, cash withdrawal, etc.)
        (F.sum(F.when(F.col("tx_category") == "betting", F.col("sent_amount"))
            .otherwise(0)) / F.sum("sent_amount")).alias("betting_spend_ratio"),
        (F.sum(F.when(F.col("tx_category") == "utility", F.col("sent_amount"))
            .otherwise(0)) / F.sum("sent_amount")).alias("utility_payment_ratio"),
        (F.sum(F.when(F.col("tx_category") == "cash_withdrawal", F.col("sent_amount"))
            .otherwise(0)) / F.sum("sent_amount")).alias("cash_withdrawal_ratio"),
        (F.sum(F.when(F.col("tx_category") == "airtime", F.col("sent_amount"))
            .otherwise(0)) / F.sum("sent_amount")).alias("airtime_spend_ratio"),
        (F.sum(F.when(F.col("tx_category") == "merchant", F.col("sent_amount"))
            .otherwise(0)) / F.sum("sent_amount")).alias("merchant_spend_ratio"),

        # P2P ratio
        (F.sum(F.when(F.col("tx_category").isin("p2p_received", "p2p_sent"), 1)
            .otherwise(0)) / F.count("*")).alias("p2p_transfer_ratio"),

        # Loan product count
        F.countDistinct(
            F.when(F.col("tx_category").isin("mshwari", "kcb_mpesa", "fuliza"),
                   F.col("tx_category"))
        ).alias("loan_product_count"),
    )
```

### 4.2 Output to Feature Store and Kafka

```python
# Write computed features to Redis (for low-latency serving)
def write_to_feature_store(batch_df, batch_id):
    """Micro-batch writer: push features to Redis + publish to Kafka."""
    import redis
    import json

    r = redis.Redis(host='redis', port=6379, db=0)
    pipe = r.pipeline()

    for row in batch_df.collect():
        key = f"features:{row['customer_id']}"
        features = row.asDict()
        features.pop("window", None)
        pipe.hset(key, mapping={k: str(v) for k, v in features.items()})
        pipe.expire(key, 86400 * 7)  # 7-day TTL

    pipe.execute()

# Trigger: process every 30 seconds
feature_query = customer_features.writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_feature_store) \
    .option("checkpointLocation", "/checkpoints/features") \
    .trigger(processingTime="30 seconds") \
    .start()
```

### 4.3 Stateful Processing: Transaction Frequency and Recency

```python
from pyspark.sql.streaming import GroupState, GroupStateTimeout

# Custom stateful aggregation for metrics that require full history
# (e.g., account_age_days, days_since_last_transaction)

@F.pandas_udf("customer_id string, account_age_days long, days_since_last long")
def compute_recency_features(key, pdf_iter):
    """Stateful UDF: track first/last transaction per customer."""
    for pdf in pdf_iter:
        customer_id = key[0]
        first_txn = pdf["transaction_at"].min()
        last_txn = pdf["transaction_at"].max()
        now = pd.Timestamp.now()
        yield pd.DataFrame({
            "customer_id": [customer_id],
            "account_age_days": [(now - first_txn).days],
            "days_since_last": [(now - last_txn).days],
        })
```

---

## 5. Feature Store for Low-Latency Serving

### 5.1 Dual-Store Architecture

| Store            | Purpose                              | Latency     | Durability   |
|------------------|--------------------------------------|-------------|--------------|
| **Redis Cluster**| Hot features for real-time scoring   | < 1 ms      | Volatile     |
| **DynamoDB**     | Durable feature history + audit log  | < 10 ms     | Persistent   |

```python
# Feature store read path (used by model serving)
import redis
import json

class FeatureStore:
    def __init__(self):
        self.redis = redis.Redis(host='redis', port=6379, db=0)
        # DynamoDB client for fallback

    def get_features(self, customer_id: str) -> dict:
        """Retrieve latest feature vector for a customer."""
        key = f"features:{customer_id}"
        raw = self.redis.hgetall(key)

        if not raw:
            # Fallback to DynamoDB for cold customers
            return self._get_from_dynamodb(customer_id)

        return {
            k.decode(): float(v.decode()) if v.decode() != 'None' else 0.0
            for k, v in raw.items()
            if k.decode() != 'customer_id'
        }

    def _get_from_dynamodb(self, customer_id: str) -> dict:
        """Fallback: read from DynamoDB feature table."""
        # Implementation with boto3
        pass
```

### 5.2 Feature Freshness Guarantees

- **P99 feature freshness:** < 60 seconds from transaction to updated feature vector
- **Redis write throughput:** ~100K writes/second per shard, well above our requirement
- **Key expiry:** 7 days TTL ensures inactive customers do not consume memory indefinitely
- **Compacted Kafka topic** (`features.computed`) provides replay capability for store recovery

---

## 6. Model Serving via FastAPI + ONNX Runtime

### 6.1 Why ONNX?

The current stack loads a joblib-serialized scikit-learn/XGBoost model on each request. This has two problems at scale:

1. **Cold start latency:** joblib deserialization on first request takes 200-500ms
2. **GIL contention:** scikit-learn inference is CPU-bound and single-threaded under Python's GIL

ONNX Runtime solves both: the model is loaded once at startup in an optimized format, and inference runs on optimized C++ kernels.

### 6.2 Model Export Pipeline

```python
# Export trained XGBoost model to ONNX format
import onnxmltools
from onnxmltools.convert import convert_xgboost
from onnxconverter_common import FloatTensorType

def export_to_onnx(model, feature_columns, output_path):
    """Convert trained XGBoost model to ONNX for serving."""
    initial_type = [('features', FloatTensorType([None, len(feature_columns)]))]
    onnx_model = convert_xgboost(model, initial_types=initial_type)
    onnxmltools.utils.save_model(onnx_model, output_path)
```

### 6.3 Real-Time Scoring Endpoint

```python
# Enhanced FastAPI model server with ONNX + Feature Store
import onnxruntime as ort
import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Credit Pulse - Real-Time Scoring")

# Load model once at startup
session = ort.InferenceSession("artifacts/credit_model.onnx")
feature_store = FeatureStore()

FEATURE_COLUMNS = [
    "transaction_count", "active_days", "transaction_frequency",
    "total_inflows", "total_outflows", "inflow_outflow_ratio",
    "avg_balance", "min_balance", "max_balance", "balance_volatility",
    "avg_received_amount", "max_received_amount", "spending_consistency",
    "days_since_last_transaction", "account_age_days",
    "betting_spend_ratio", "utility_payment_ratio", "cash_withdrawal_ratio",
    "airtime_spend_ratio", "merchant_spend_ratio", "p2p_transfer_ratio",
    "loan_product_count",
]

@app.post("/api/score/{customer_id}")
async def score_realtime(customer_id: str):
    """Score a customer using live features from the feature store."""
    # 1. Fetch latest features (< 1ms from Redis)
    features = feature_store.get_features(customer_id)
    if not features:
        raise HTTPException(status_code=404, detail="No features found for customer")

    # 2. Build feature vector in correct column order
    feature_vector = np.array(
        [[features.get(col, 0.0) for col in FEATURE_COLUMNS]],
        dtype=np.float32
    )

    # 3. Run ONNX inference (< 1ms)
    input_name = session.get_inputs()[0].name
    result = session.run(None, {input_name: feature_vector})
    probabilities = result[1][0]  # [p_no_default, p_default]
    risk_score = float(probabilities[1])

    # 4. Determine risk label (same logic as current system)
    if risk_score > 0.5:
        risk_label = "high"
    elif risk_score > 0.3:
        risk_label = "medium"
    else:
        risk_label = "low"

    return {
        "customer_id": customer_id,
        "risk_score": risk_score,
        "risk_label": risk_label,
        "default_probability": risk_score,
        "feature_freshness_seconds": features.get("_updated_at", "unknown"),
        "model_version": "v2.1-onnx",
    }
```

### 6.4 Performance Targets

| Metric                  | Current (Batch)  | Target (Real-Time) |
|-------------------------|------------------|---------------------|
| Feature freshness       | Hours            | < 60 seconds        |
| Scoring latency (P50)   | ~50ms            | < 5ms               |
| Scoring latency (P99)   | ~200ms           | < 20ms              |
| Throughput              | ~100 req/s       | > 5,000 req/s       |
| Availability            | Single process   | 99.9%               |

---

## 7. Alternative: TensorFlow Serving for Neural Network Models

If the model architecture evolves to include deep learning components (e.g., LSTM for transaction sequence modeling), TensorFlow Serving provides:

- **gRPC interface** with ~2x lower latency than REST
- **Model versioning** with automatic A/B routing
- **GPU inference** for sequence models
- **Batching** to amortize overhead across concurrent requests

```bash
# Deploy TensorFlow Serving with Docker
docker run -p 8501:8501 \
  --mount type=bind,source=/models/credit_pulse,target=/models/credit_pulse \
  -e MODEL_NAME=credit_pulse \
  tensorflow/serving:latest
```

This becomes relevant when transitioning from gradient boosting (XGBoost) to deep learning models that process raw transaction sequences rather than pre-aggregated features.

---

## 8. Monitoring and Data Quality

### 8.1 Great Expectations for Stream Data Quality

```python
import great_expectations as ge

# Data quality checks on each micro-batch
def validate_micro_batch(batch_df, batch_id):
    """Run GE validations on each Spark micro-batch."""
    pdf = batch_df.toPandas()
    ge_df = ge.from_pandas(pdf)

    # Structural checks
    assert ge_df.expect_column_values_to_not_be_null("customer_id").success
    assert ge_df.expect_column_values_to_not_be_null("transaction_id").success

    # Value range checks
    assert ge_df.expect_column_values_to_be_between(
        "received_amount", min_value=0, max_value=10_000_000
    ).success
    assert ge_df.expect_column_values_to_be_between(
        "sent_amount", min_value=0, max_value=10_000_000
    ).success

    # Categorical checks
    valid_categories = [
        "airtime", "betting", "utility", "cash_withdrawal",
        "mshwari", "kcb_mpesa", "fuliza", "p2p_received",
        "p2p_sent", "merchant", "other"
    ]
    assert ge_df.expect_column_values_to_be_in_set(
        "tx_category", valid_categories
    ).success

    # Statistical drift detection
    assert ge_df.expect_column_mean_to_be_between(
        "sent_amount", min_value=10, max_value=100_000
    ).success
```

### 8.2 Operational Monitoring Stack

[![Monitoring & Alerting Stack](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=P-YZfTh3Ijk2AvzKRm8qy,ue_leQFkZJyyknkZIary6w)

> **[Open interactive diagram](https://excalidraw.com/#json=P-YZfTh3Ijk2AvzKRm8qy,ue_leQFkZJyyknkZIary6w)** — Metric Sources (Spark, Kafka, FastAPI) → Prometheus → Grafana / AlertManager → PagerDuty + Slack, with Great Expectations (DQ) and Evidently AI (drift detection)

**Key metrics to monitor:**

| Metric                          | Threshold              | Action                      |
|---------------------------------|------------------------|-----------------------------|
| Kafka consumer lag              | > 10,000 messages      | Scale Spark executors        |
| Feature compute latency (P99)   | > 60 seconds           | Investigate bottleneck       |
| Scoring latency (P99)           | > 50ms                 | Add API replicas             |
| Data quality failure rate       | > 1% of micro-batches  | Alert on-call engineer       |
| Model prediction drift          | PSI > 0.2              | Trigger model retraining     |
| Redis memory utilization        | > 80%                  | Scale Redis cluster          |

### 8.3 Model Performance Monitoring

```python
# Track prediction distribution and trigger retraining
from evidently import ColumnMapping
from evidently.metric_preset import DataDriftPreset

def monitor_model_drift(reference_df, production_df):
    """Compare production predictions against reference distribution."""
    column_mapping = ColumnMapping(
        prediction="risk_score",
        numerical_features=FEATURE_COLUMNS,
    )
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=production_df,
               column_mapping=column_mapping)

    drift_detected = report.as_dict()["metrics"][0]["result"]["dataset_drift"]
    if drift_detected:
        trigger_retraining_pipeline()
```

---

## 9. Infrastructure: Kubernetes and Auto-Scaling

### 9.1 Kubernetes Deployment Architecture

```yaml
# Namespace: credit-pulse-prod
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scoring-api
  namespace: credit-pulse-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: scoring-api
  template:
    metadata:
      labels:
        app: scoring-api
    spec:
      containers:
      - name: scoring-api
        image: credit-pulse/scoring-api:v2.1
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        env:
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: feature-store-config
              key: redis_host
        - name: MODEL_PATH
          value: "/models/credit_model.onnx"
        volumeMounts:
        - name: model-volume
          mountPath: /models
      volumes:
      - name: model-volume
        persistentVolumeClaim:
          claimName: model-pvc
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scoring-api-hpa
  namespace: credit-pulse-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scoring-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Pods
    pods:
      metric:
        name: http_request_latency_p99
      target:
        type: AverageValue
        averageValue: "20m"  # 20ms
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 120
```

### 9.2 Spark on Kubernetes

```yaml
# SparkApplication CRD (spark-operator)
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: feature-stream
  namespace: credit-pulse-prod
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster
  image: credit-pulse/spark-jobs:v2.1
  mainApplicationFile: "local:///app/feature_stream.py"
  sparkVersion: "3.5.0"
  driver:
    cores: 1
    memory: "2g"
  executor:
    cores: 2
    instances: 3
    memory: "4g"
  dynamicAllocation:
    enabled: true
    initialExecutors: 3
    minExecutors: 2
    maxExecutors: 10
```

### 9.3 Infrastructure Sizing for 1M+ Transactions/Day

| Component              | Sizing                                  | Cost Estimate (AWS) |
|------------------------|-----------------------------------------|---------------------|
| Kafka (MSK)            | 3 brokers, m5.large, 500GB EBS each     | ~$900/month         |
| Spark (EKS)            | 3-10 executors, m5.xlarge, dynamic       | ~$1,200/month       |
| Redis (ElastiCache)    | 3-node cluster, r6g.large                | ~$600/month         |
| DynamoDB               | On-demand, ~1M writes/day               | ~$150/month         |
| API (EKS)              | 3-20 pods, c5.xlarge nodes               | ~$800/month         |
| S3 (data lake)         | ~500GB/month ingestion                   | ~$15/month          |
| Monitoring             | Prometheus + Grafana on EKS              | ~$200/month         |
| **Total**              |                                          | **~$3,865/month**   |

---

## 10. Migration Strategy: Batch to Streaming

### Phase 1: Dual-Write (Weeks 1-4)

Run batch and streaming pipelines in parallel. The batch pipeline remains the source of truth.

[![Migration Strategy](https://img.shields.io/badge/View_Diagram-Excalidraw-6965db)](https://excalidraw.com/#json=inbSthQpBWtGVOMeKAdy-,ejq38w-OoCLiXNNTwxIfig)

> **[Open interactive diagram](https://excalidraw.com/#json=inbSthQpBWtGVOMeKAdy-,ejq38w-OoCLiXNNTwxIfig)** — 4-phase migration: Phase 1 Dual-Write (batch + shadow streaming) → Phase 2 Shadow Scoring (ONNX, log-only) → Phase 3 Gradual Cutover (5% → 25% → 50% → 100%) → Phase 4 Optimization

**Key activities:**
- Deploy Kafka and produce events alongside batch ingestion
- Run Spark streaming to compute features into a shadow Redis store
- Compare batch-computed features vs stream-computed features for correctness
- Fix any discrepancies in the streaming logic

### Phase 2: Shadow Scoring (Weeks 5-8)

The streaming pipeline computes features and scores, but results are logged -- not served to production.

**Key activities:**
- Export the XGBoost model to ONNX format
- Deploy ONNX-based scoring service alongside the existing FastAPI server
- Route a copy of production traffic to the streaming scorer
- Compare risk scores between batch and streaming paths
- Validate that P99 latency targets are met under production traffic patterns

### Phase 3: Cutover (Weeks 9-12)

Gradually shift production traffic to the real-time pipeline.

**Key activities:**
- Canary deployment: route 5% -> 25% -> 50% -> 100% of traffic to streaming scorer
- Monitor for score divergence, latency regressions, and feature freshness
- Decommission the batch feature pipeline (keep batch for model retraining)
- Retain DuckDB + dbt for ad-hoc analytics and historical analysis

### Phase 4: Optimization (Weeks 13-16)

**Key activities:**
- Tune Spark Structured Streaming watermarks and trigger intervals
- Implement exactly-once semantics with Kafka transactional writes
- Add automated model retraining triggered by drift detection
- Implement feature backfill pipelines for new features
- Load testing at 2x-5x expected peak throughput

---

## 11. Summary

| Dimension                 | Current State                      | Future State                               |
|---------------------------|------------------------------------|--------------------------------------------|
| **Ingestion**             | CSV/XLSX file loads                | Kafka event streams                        |
| **Processing**            | dbt batch SQL on DuckDB           | PySpark Structured Streaming               |
| **Feature freshness**     | Hours (full batch re-run)          | < 60 seconds                               |
| **Feature storage**       | DuckDB tables                     | Redis (hot) + DynamoDB (cold)              |
| **Model format**          | joblib (scikit-learn/XGBoost)      | ONNX Runtime                               |
| **Scoring latency**       | ~50-200ms                          | < 5ms (P50), < 20ms (P99)                 |
| **Scalability**           | Single node                        | Horizontal auto-scaling on Kubernetes      |
| **Monitoring**            | Print statements                   | Prometheus + Grafana + PagerDuty           |
| **Data quality**          | Manual inspection                  | Great Expectations on every micro-batch    |
| **Throughput**            | ~100 req/s                         | > 5,000 req/s                              |
| **Cost**                  | $0 (local dev)                     | ~$3,865/month (AWS)                        |

The migration preserves the existing 22-feature credit scoring model and risk segmentation logic while delivering sub-second feature freshness and single-digit millisecond scoring latency -- enabling Credit Pulse to support real-time loan decisioning for 1M+ daily M-Pesa transactions.
