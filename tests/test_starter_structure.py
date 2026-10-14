import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "selected" / "variant_manifest.json"
OUTPUT_EXTENSIONS = {".csv", ".png", ".jpg", ".jpeg"}


def test_variant_selector_creates_manifest_and_dataset(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / "src"))
    import variant_selector

    monkeypatch.setattr(variant_selector, "SELECTED_DIR", tmp_path)
    monkeypatch.setattr(variant_selector, "MANIFEST_PATH", tmp_path / "variant_manifest.json")

    manifest = variant_selector.select_variant()
    dataset_path = variant_selector.generate_dataset(manifest)

    assert dataset_path.exists()
    assert manifest["id"].startswith("greenhouse-")
    assert manifest["fault_zone"] in {"north-bed", "south-bed"}


def test_analysis_helpers_load_and_summarise_selected_dataset():
    sys.path.insert(0, str(ROOT / "src"))

    from iot_analysis import count_anomalies, load_rows, numeric_summary

    if not MANIFEST_PATH.exists():
        pytest.skip("Run python src/variant_selector.py before checking the selected dataset.")

    manifest = json.loads(MANIFEST_PATH.read_text())
    rows = load_rows(ROOT / "data" / "selected" / manifest["dataset_file"])
    summary = numeric_summary(rows)
    anomalies = count_anomalies(rows)
    zones = {row["zone"] for row in rows}

    assert len(rows) == 336
    assert zones == {"north-bed", "south-bed"}
    assert "air_temperature_c" in summary
    assert "device_battery_pct" in summary
    assert "normal" in anomalies
    assert any(label != "normal" for label in anomalies)
    assert sum(anomalies.values()) == 336


def test_required_student_files_are_present():
    assert (ROOT / "notebooks" / "ITC560_A4_analysis.ipynb").exists()
    assert (ROOT / "report" / "ITC560_A4_report_template.md").exists()
    assert (ROOT / ".devcontainer" / "devcontainer.json").exists()
    assert (ROOT / ".vscode" / "settings.json").exists()
    assert (ROOT / ".github" / "workflows" / "starter-checks.yml").exists()


def test_completed_submission_evidence_is_present_after_variant_selection():
    if not MANIFEST_PATH.exists():
        pytest.skip("Submission evidence checks run after the selected variant exists.")

    output_files = [
        path
        for path in (ROOT / "outputs").iterdir()
        if path.is_file() and path.suffix.lower() in OUTPUT_EXTENSIONS
    ]
    report_path = ROOT / "report" / "ITC560_A4_report.md"

    assert len(output_files) >= 4, "Save at least four useful chart or table files in outputs/."
    assert report_path.exists(), "Commit a report evidence draft at report/ITC560_A4_report.md."


def test_completed_notebook_executes_after_variant_selection(tmp_path):
    if not MANIFEST_PATH.exists():
        pytest.skip("Notebook execution checks run after the selected variant exists.")

    output_path = tmp_path / "executed_notebook.ipynb"
    command = [
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "notebooks/ITC560_A4_analysis.ipynb",
        "--output",
        str(output_path),
    ]

    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, (
        "The notebook must run from top to bottom without errors.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )
    assert output_path.exists()
