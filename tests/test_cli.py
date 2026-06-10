from pathlib import Path

from typer.testing import CliRunner

from griffin.cli import app

runner = CliRunner()


def test_cli_doctor_works():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "griffin_version" in result.stdout


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
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (run_dir / "outputs" / "candidates.csv").exists()
    assert (run_dir / "run_manifest.json").exists()
    resumed = runner.invoke(app, ["resume", "--run-dir", str(run_dir)])
    assert resumed.exit_code == 0, resumed.stdout
