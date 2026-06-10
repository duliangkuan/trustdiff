import json
import os

from report_export import export_report

EVENTS = [
    {"kind": "click"},
    {"kind": "view"},
    {"kind": "click"},
]


def test_export_report_writes_file(tmp_path):
    path = os.path.join(tmp_path, "report.json")
    export_report(EVENTS, path=path)
    with open(path, "r", encoding="utf-8") as fh:
        report = json.load(fh)
    assert report["generated"] is True
    assert report["summary"]["total"] == 3
    assert report["headline"] == "3 events"
