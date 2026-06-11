# AWS patterns for ML systems (EKS/ECS-centric)

Detailed service selection guidance. Assume the team runs EKS/ECS rather than SageMaker.

## Model serving

| Workload | Default | Notes |
|---|---|---|
| GBM / small classical models | FastAPI or gRPC service, ONNX Runtime, CPU nodes on EKS | Convert XGBoost/LightGBM to ONNX or use treelite; sub-ms inference, scale with HPA on RPS |
| Transformer encoders (classification, embeddings) | Triton Inference Server on GPU node group | Dynamic batching is the main lever — tune max_batch_size and queue delay against the p99 budget |
| LLM generation | vLLM on EKS (or TGI) | Scale on in-flight tokens / queue depth, never CPU. Use continuous batching; pin tokenizer + weights in one image or S3 artifact pulled at startup |
| Batch scoring | K8s Jobs or Argo Workflows reading/writing S3 | Spot instances + checkpointed shards; idempotent partitions so retries are safe |

Serving rules of thumb:

- HPA on custom metrics via Prometheus Adapter or KEDA; GPU utilization is a lagging signal, queue depth leads.
- One model per deployment. Multi-model servers save cost but couple rollbacks; only do it for many small models (Triton model repository).
- Always expose: model version header in responses, per-version request/latency/error metrics, and prediction logging (sampled) to Kinesis Firehose → S3.

## Training infrastructure

- **Orchestration**: Argo Workflows on EKS for ML-native DAGs; Step Functions when the pipeline crosses many AWS services and the team prefers managed state. Avoid two orchestrators in one pipeline.
- **GPU provisioning**: Karpenter node pools with separate provisioners for spot (training) and on-demand (serving). Checkpoint to S3 every N steps so spot reclamation costs minutes, not hours.
- **Distributed training**: torchrun via the Kubeflow Training Operator (PyTorchJob) or plain StatefulSets. FSDP for >1 GPU memory footprints; NCCL over EFA only matters at multi-node scale — single-node multi-GPU first.
- **Artifacts**: every run writes (code SHA, data snapshot manifest, config, metrics, checkpoint) to S3 under an immutable run ID. MLflow or W&B for tracking; if neither exists, a JSON manifest convention in S3 is acceptable and better than nothing.

## Feature and data infrastructure

- **Offline store**: S3 + Iceberg tables, computed by Spark (EMR or EMR-on-EKS) or Athena CTAS for lighter aggregations. Partition by event date; never by ingestion date if labels arrive late.
- **Online store**: DynamoDB for key-value feature reads at scale (single-digit ms, pay-per-request to start); ElastiCache Redis when reads are extremely hot or features are large/composite.
- **Streaming features**: only when the freshness analysis demands it. Flink on Kinesis (or MSK) computing windowed aggregates, dual-written to the online store and to S3 for training parity. The parity write is non-negotiable — it is what prevents train/serve skew.
- **Log-and-wait**: when a feature store is too heavy, log the exact feature vector served at prediction time and train on those logs. Cheapest reliable way to eliminate skew; costs label-join complexity.

## Embeddings and retrieval

- OpenSearch k-NN (HNSW): managed, fine to ~100M vectors, good when the team wants filters + hybrid BM25.
- Self-hosted Qdrant on EKS: better recall/latency tuning, cheaper at high QPS, more ops burden.
- FAISS in-process: best for batch jobs and static indexes rebuilt offline; avoid for mutable online indexes.
- Always version the embedding model with the index. Querying an index with embeddings from a different model version is a silent correctness bug — store model version in index metadata and assert at query time.

## Cost levers, in order of impact

1. Spot for all interruptible compute (training, batch scoring) with checkpointing.
2. Right-size GPU per workload: encoders rarely need more than A10G/L4; reserve A100/H100-class for LLM training and high-throughput generation.
3. Dynamic batching at serving (often 2-5x throughput on the same hardware).
4. Quantization: int8/AWQ for LLM serving, ONNX int8 for encoders — validate quality on the eval suite before shipping.
5. Cache layer in front of expensive inference (exact-match first; semantic cache only with hit-rate evidence).

## Observability minimums

Every production ML service ships with: request/latency/error metrics per model version, prediction distribution monitors (mean score, score histogram drift), feature null-rate and range monitors at serving time, and sampled prediction logs joined to outcomes for continuous evaluation. Alerts page on serving errors and feature pipeline lag; drift alerts go to a dashboard/ticket, not a page, unless tied to a guardrail metric.
