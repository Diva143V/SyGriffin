from pathlib import Path

import requests
from typer.testing import CliRunner

import griffin.adapters.llm.ollama as ollama_module
from griffin.cli import app

runner = CliRunner()


def test_cli_doctor_works():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "griffin_version" in result.stdout
    assert "mhcflurry_available" in result.stdout
    assert "ollama_reachable" in result.stdout
    assert "default_ollama_model" in result.stdout


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


def test_non_mock_run_fails_clearly_without_mhcflurry(fixture_dir: Path, tmp_path: Path):
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


def test_ollama_mode_fails_clearly_when_unreachable(
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
    assert result.exit_code != 0
    assert "Ollama LLM unavailable" in result.stdout + result.stderr
