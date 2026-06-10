# feat: sales report export

Finance asked for a way to pull the revenue roll-ups out of the system without
going through the API. This PR adds `services/reporting_export.py`, which reads
the figures from the reporting service and renders them to a JSON file in a
shared export directory (default `data/`).

Includes tests for the payload shape and for the on-disk file being written
and re-readable.
