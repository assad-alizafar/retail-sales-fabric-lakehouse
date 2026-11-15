# Reproduce and validate the project

You do not need this folder to understand the project; start with the [main README](../README.md) or [results](../3-Project-Results/).

- [**Fabric deployment instructions**](guides/FABRIC_SETUP.md): run the notebooks in a Lakehouse
- [**Fabric pipeline instructions**](guides/PIPELINE_SETUP.md): connect the notebook activities
- [**Data dictionary**](guides/DATA_DICTIONARY.md): definitions and rules
- [**Python reference implementation**](local_python/): regenerate or inspect local results
- [**Automated tests**](automated_tests/): verify reconciliation and quality rules
- [**SQL business queries**](business_sql/gold_business_queries.sql): Gold analysis examples
- [**Fabric configuration**](fabric_configuration/): illustrative design/config files

From the repository root:

```bash
python -m pip install -r 4-Setup-and-Testing/requirements-local.txt
python 4-Setup-and-Testing/local_python/run_local_demo.py --source 2-Sample-Retail-Data --output 3-Project-Results/local-run
python -m pytest 4-Setup-and-Testing/automated_tests -q
```
