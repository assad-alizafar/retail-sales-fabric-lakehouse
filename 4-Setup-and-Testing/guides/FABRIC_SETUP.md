# Deploy and run in Microsoft Fabric

## Prerequisites

- Access to a Microsoft Fabric workspace assigned to a supported capacity/trial with Spark enabled.
- Permission to create a Lakehouse, notebooks, and a Data Factory pipeline.
- No external credentials: source data is generated locally and uploaded manually.

## Manual run (recommended for a first portfolio demonstration)

1. Create a Fabric workspace and a Lakehouse named **RetailAnalyticsLakehouse** (name is illustrative).
2. In the Lakehouse, create folder path **Files/source/ecommerce/**.
3. Upload all four CSV files from `2-Sample-Retail-Data/` into that folder.
4. Import the supplied notebook files from `1-Fabric-Notebooks/` into your Fabric workspace, or create four notebooks and paste/import their cells.
5. **Attach the same Lakehouse as the default Lakehouse to each notebook**, and restart the Spark session if Fabric prompts you.
6. Run notebooks in order: `01_Bronze_Ingestion.ipynb` → `02_Silver_Validation.ipynb` → `03_Gold_Business_Marts.ipynb` → `04_Data_Quality_Checks.ipynb`.
7. Confirm 11 managed Delta tables: Bronze 4, Silver 4, Gold 3. Review printed row counts and quality checks.
8. In the Lakehouse SQL analytics endpoint, use `4-Setup-and-Testing/business_sql/gold_business_queries.sql` for sample queries.
9. Capture your actual Fabric screenshots (Lakehouse table list, notebook run status, pipeline run, SQL endpoint results); place **only genuine screenshots** in `3-Project-Results/visuals/screenshots/` when publishing.

## Pipeline scheduling

Follow `4-Setup-and-Testing/guides/PIPELINE_SETUP.md` to create a native Fabric pipeline with four dependent Notebook activities. This repository provides a **configuration specification**, not a workspace-ready Fabric pipeline export. Item IDs and bindings are assigned by your tenant.

## Storage and refresh behavior

- All four notebooks write managed Delta tables under the attached Lakehouse using `saveAsTable`.
- Bronze/Silver/Gold layers are represented by *table name prefixes* inside one Lakehouse; this is a portfolio-friendly logical medallion, rather than physically isolated workspaces or Lakehouses.
- Runs use deterministic **full-refresh overwrite**, so reruns do not append duplicates. This is a batch ELT demonstration, not an incremental/CDC solution.
- If a source schema changes, review the schema and downstream transformations before rerunning; `overwriteSchema` is used intentionally for this demo.
- Do not use production personal data; this project is synthetic.

## Validation status

The local Pandas reference implementation and pytest suite can be executed outside Fabric. The actual Spark notebooks and Microsoft Fabric orchestration must be run and verified in your own tenant; GitHub Actions does not execute Fabric jobs.

## Relevant Microsoft documentation

- https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-and-delta-tables
- https://learn.microsoft.com/en-us/fabric/data-factory/notebook-activity
- https://learn.microsoft.com/en-us/fabric/data-engineering/notebookutils/notebookutils-file-system
