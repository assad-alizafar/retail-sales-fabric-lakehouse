# Next engineering iterations

The core repository intentionally uses a deterministic batch/full-refresh pipeline. To move toward an enterprise scenario, implement and **test** these as separate, clearly labeled milestones:

1. Incremental ingestion using a watermark and persisted audit/checkpoint table.
2. `MERGE INTO` Delta Silver targets with deterministic latest-version rules.
3. Quarantine tables for bad rows and configurable DQ thresholds.
4. Partitioning, compaction, V-Order / OPTIMIZE evaluation, and measured before/after timings.
5. Fabric Git integration, workspace-specific deployment and environment parameterization.
6. Slowly-changing dimension Type 2 for customer region history.
7. Real data sources with secret management instead of synthetic CSVs.

Do not include these features as accomplished work on your resume until implemented and measured.
