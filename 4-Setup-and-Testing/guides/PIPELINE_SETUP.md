# Native Data Factory pipeline setup (Fabric)

This project includes four importable PySpark notebooks and a **template describing the pipeline activities**. Fabric assigns notebook and workspace item IDs, so no portable native Fabric pipeline item is claimed here.

1. In your Fabric workspace, select **New → Data pipeline**. Name it `PL_Retail_Medallion_Batch`.
2. Add Notebook activity `NB_Bronze_Ingestion`, choose `01_Bronze_Ingestion`.
3. Add Notebook activity `NB_Silver_Validation`, choose `02_Silver_Validation`.
4. Add Notebook activity `NB_Gold_Business_Marts`, choose `03_Gold_Business_Marts`.
5. Add Notebook activity `NB_Data_Quality_Checks`, choose `04_Data_Quality_Checks`.
6. Connect the activities **sequentially on Success** (green dependencies). Do not run Silver before Bronze finishes.
7. Validate and run. Review activity output and verify the final DQ notebook raises no assertion error.
8. Only after a successful manual run, optionally add a schedule trigger using your tenant's supported scheduling UI.
9. Document the actual run time, table counts, and pipeline status with tenant screenshots.

See `4-Setup-and-Testing/fabric_configuration/pipeline_activity_spec.json` for the intended notebook activity graph. This is a portable design document, **not** an importable Fabric pipeline JSON.

**Handling failures:** failed notebooks stop subsequent activities due to Success-only dependencies. Fix the cause and rerun; table loads are idempotent overwrite operations in this demonstration.

**Operational improvement ideas:** add run IDs and audit Delta tables, notifications, schema contracts, change-data capture, SLA alerts and a parameterized source path before claiming production readiness.
