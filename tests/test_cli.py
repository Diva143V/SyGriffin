import json
from pathlib import Path

import requests
from typer.testing import CliRunner

import griffin.adapters.llm.ollama as ollama_module
from griffin.adapters.mhc.mhcflurry import MHCflurryPredictor
from griffin.cli import app

runner = CliRunner()


def test_cli_doctor_works():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "griffin_version" in result.stdout
    assert "mhcflurry_available" in result.stdout
    assert "ollama_reachable" in result.stdout
    assert "default_ollama_model" in result.stdout
    assert "scientific_python_recommended" in result.stdout


def test_doctor_reports_reachable_ollama_models(monkeypatch):
    calls = []

    class Response:
        ok = True

        def json(self):
            return {"models": [{"name": "phi3:latest"}, {"name": "llama3.2:latest"}]}

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return Response()

    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setattr(ollama_module.requests, "get", fake_get)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["ollama_reachable"] is True
    assert data["ollama_base_url"] == "http://127.0.0.1:11434"
    assert data["available_ollama_models"] == ["phi3:latest", "llama3.2:latest"]
    assert calls[0] == ("http://127.0.0.1:11434/api/tags", 2)


def test_doctor_falls_back_to_localhost_for_ollama(monkeypatch):
    calls = []

    class Response:
        ok = True

        def json(self):
            return {"models": [{"name": "phi3"}]}

    def fake_get(url, timeout):
        calls.append((url, timeout))
        if url.startswith("http://127.0.0.1:11434"):
            raise requests.ConnectionError("127 unavailable")
        return Response()

    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setattr(ollama_module.requests, "get", fake_get)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["ollama_reachable"] is True
    assert data["ollama_base_url"] == "http://localhost:11434"
    assert data["available_ollama_models"] == ["phi3"]
    assert calls == [
        ("http://127.0.0.1:11434/api/tags", 2),
        ("http://localhost:11434/api/tags", 2),
    ]


def test_doctor_reports_unreachable_ollama(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("not running")

    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setattr(ollama_module.requests, "get", raise_connection_error)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["ollama_reachable"] is False
    assert data["ollama_base_url"] == "http://127.0.0.1:11434"
    assert data["available_ollama_models"] == []


def test_doctor_uses_ollama_base_url_env(monkeypatch):
    calls = []

    class Response:
        ok = True

        def json(self):
            return {"models": [{"name": "phi3"}]}

    def fake_get(url, timeout):
        calls.append((url, timeout))
        return Response()

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11435")
    monkeypatch.setattr(ollama_module.requests, "get", fake_get)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["ollama_reachable"] is True
    assert data["ollama_base_url"] == "http://127.0.0.1:11435"
    assert calls == [("http://127.0.0.1:11435/api/tags", 2)]


def test_init_creates_expected_folders(tmp_path: Path):
    result = runner.invoke(app, ["init", "--project-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".griffin" / "config.yaml").exists()
    assert (tmp_path / "runs").exists()


def test_validate_input_works(fixture_dir: Path):
    result = runner.invoke(
        app,
        [
            "validate-input",
            "--vcf",
            str(fixture_dir / "tiny.vcf"),
            "--hla",
            "HLA-A*02:01",
            "--cancer-type",
            "melanoma",
        ],
    )
    assert result.exit_code == 0
    assert "Input valid" in result.stdout


def test_run_end_to_end_and_resume(fixture_dir: Path, tmp_path: Path):
    run_dir = tmp_path / "demo"
    result = runner.invoke(
        app,
        [
            "run",
            "--vcf",
            str(fixture_dir / "tiny.vcf"),
            "--hla",
            "HLA-A*02:01",
            "--cancer-type",
            "melanoma",
            "--sample-id",
            "demo",
            "--out",
            str(run_dir),
            "--mock",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (run_dir / "outputs" / "candidates.csv").exists()
    assert (run_dir / "run_manifest.json").exists()
    resumed = runner.invoke(app, ["resume", "--run-dir", str(run_dir)])
    assert resumed.exit_code == 0, resumed.stdout


def test_non_mock_run_fails_clearly_without_mhcflurry(
    fixture_dir: Path, tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(MHCflurryPredictor, "available", lambda self: False)
    result = runner.invoke(
        app,
        [
            "run",
            "--vcf",
            str(fixture_dir / "tiny.vcf"),
            "--hla",
            "HLA-A*02:01",
            "--cancer-type",
            "melanoma",
            "--sample-id",
            "demo",
            "--out",
            str(tmp_path / "nonmock"),
        ],
    )
    assert result.exit_code != 0
    output = result.stdout + result.stderr
    assert "MHC predictor unavailable." in output
    assert "--mock" in output


def test_ollama_mode_with_mock_evidence_uses_safe_static_summary(
    fixture_dir: Path, tmp_path: Path, monkeypatch
):
    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("not running")

    monkeypatch.setattr(ollama_module.requests, "get", raise_connection_error)
    result = runner.invoke(
        app,
        [
            "run",
            "--vcf",
            str(fixture_dir / "tiny.vcf"),
            "--hla",
            "HLA-A*02:01",
            "--cancer-type",
            "melanoma",
            "--sample-id",
            "demo",
            "--out",
            str(tmp_path / "ollama"),
            "--mock",
            "--use-llm",
            "--llm-provider",
            "ollama",
            "--ollama-model",
            "phi3",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    manifest = json.loads((tmp_path / "ollama" / "manifest.json").read_text(encoding="utf-8"))
    assert (
        manifest["parameters"]["llm_summary"]
        == "This run used mock evidence records for demo/testing only. No real PubMed or "
        "ClinicalTrials.gov records were retrieved."
    )
