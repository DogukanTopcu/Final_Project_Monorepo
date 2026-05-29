"""Shared sandbox execution utilities for coding benchmarks.

Two execution modes:
  - run_function_tests: HumanEval+ style — complete a function body, run
    a check(candidate) harness, pass if it exits 0.
  - run_io_tests: LiveCodeBench style — complete program, feed each test
    case via stdin, compare stdout to expected output.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap

from core.prompt import normalize_code_answer


def strip_code_fences(text: str) -> str:
    """Normalize code output by removing Markdown-only wrapper lines.

    The returned string preserves code indentation so function bodies remain
    executable after normalization.
    """
    return normalize_code_answer(text) or ""


def run_function_tests(
    prompt: str,
    code: str,
    test_code: str,
    entry_point: str,
    timeout: int = 10,
) -> bool:
    """Run model-generated function body against a check(candidate) harness.

    Assembles: prompt (signature + docstring) + code (body) + test_code +
    check(entry_point). Returns True if the subprocess exits 0.
    """
    full_program = textwrap.dedent(f"""\
{prompt}
{code}

{test_code}

check({entry_point})
""")
    return _run_subprocess(full_program, stdin_data=None, timeout=timeout) == 0


def run_io_tests(
    code: str,
    test_cases: list[dict],
    timeout: int = 10,
) -> bool:
    """Run model-generated program against all public stdin/stdout test cases.

    Returns True only when every test case produces the expected output.
    Output comparison strips trailing whitespace on both sides.
    """
    for tc in test_cases:
        stdin_data = str(tc.get("input", ""))
        expected = str(tc.get("output", "")).strip()
        actual = _run_subprocess_capture(code, stdin_data=stdin_data, timeout=timeout)
        if actual is None or actual.strip() != expected:
            return False
    return True


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _write_temp(code: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        return f.name


def _run_subprocess(code: str, stdin_data: str | None, timeout: int) -> int:
    """Return exit code. Returns 1 on timeout or OS error."""
    fname = _write_temp(code)
    try:
        result = subprocess.run(
            [sys.executable, fname],
            input=stdin_data or "",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        return 1
    except Exception:
        return 1
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass


def _run_subprocess_capture(code: str, stdin_data: str, timeout: int) -> str | None:
    """Return stdout string, or None on timeout / error."""
    fname = _write_temp(code)
    try:
        result = subprocess.run(
            [sys.executable, fname],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None
    finally:
        try:
            os.unlink(fname)
        except OSError:
            pass
