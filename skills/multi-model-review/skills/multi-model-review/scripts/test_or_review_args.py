"""
Argparse contract tests for or_review.py.
Run: python -m pytest test_or_review_args.py -v
"""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent / "or_review.py"


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_models_required_without_it_exits_nonzero():
    """--models is now required; no --models → argparse error (exit 2)."""
    r = run(["--prompt", "hello"])
    assert r.returncode != 0
    assert "required" in r.stderr.lower() or "error" in r.stderr.lower()


def test_preset_flag_is_gone():
    """--preset must no longer exist as a valid argument."""
    r = run(["--preset", "code", "--prompt", "hello"])
    assert r.returncode != 0
    assert "unrecognized" in r.stderr.lower() or "error" in r.stderr.lower()


def test_list_presets_flag_is_gone():
    """--list-presets must no longer exist."""
    r = run(["--list-presets"])
    assert r.returncode != 0
    assert "unrecognized" in r.stderr.lower() or "error" in r.stderr.lower()


def test_models_and_prompt_accepted():
    """--models + --prompt (no API key) should fail on missing key, not on arg parsing."""
    r = run(["--models", "openai/gpt-5.5", "--prompt", "hello"])
    assert "unrecognized arguments" not in r.stderr
    assert "invalid choice" not in r.stderr
    assert r.returncode != 2  # exit 2 = argparse error


def test_system_flag_still_works():
    """--system is still accepted (no argparse error)."""
    r = run(["--models", "openai/gpt-5.5", "--prompt", "x", "--system", "You are an expert."])
    assert "unrecognized arguments" not in r.stderr
    assert "invalid choice" not in r.stderr
    assert r.returncode != 2  # exit 2 = argparse error
