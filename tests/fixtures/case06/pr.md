# feat: export a statistics report

Ops asked for a quick way to dump the current usage stats to a JSON report
they can hand off to finance. This PR adds a `report_export` module with an
`export_report(events)` helper that builds a small report payload (totals
plus a one-line headline) and writes it to `data/report.json`.

Includes a test that runs the export against a temp path and checks the
report contents.
