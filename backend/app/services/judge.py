from __future__ import annotations

import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.submission import Submission
from app.models.testcase import TestCase
from app.services.submissions import mark_submission


@dataclass
class JudgeResult:
    status: str
    score: int
    time_ms: int
    error_message: str | None = None


def normalize_output(value: str) -> str:
    lines = [line.rstrip() for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def judge_submission(submission: Submission, db: Session) -> Submission:
    mark_submission(submission, db, status="RUNNING", score=0)
    test_cases = sorted(submission.problem.test_cases, key=lambda item: (item.sort_order, item.id))
    if not test_cases:
        return mark_submission(
            submission,
            db,
            status="RE",
            score=0,
            error_message="No test cases configured for this problem.",
        )

    result = _run_cases(submission, test_cases)
    return mark_submission(
        submission,
        db,
        status=result.status,
        score=result.score,
        time_ms=result.time_ms,
        memory_kb=None,
        error_message=result.error_message,
    )


def _run_cases(submission: Submission, test_cases: list[TestCase]) -> JudgeResult:
    settings = get_settings()
    work_root = settings.judge_workspace
    work_root.mkdir(parents=True, exist_ok=True)
    workdir = work_root / f"sub_{submission.id}_{uuid.uuid4().hex}"
    workdir.mkdir(parents=True)
    started = time.perf_counter()

    try:
        command = _prepare_command(submission.language, submission.code, workdir)
        if command.status != "READY":
            return JudgeResult(command.status, 0, _elapsed_ms(started), command.error_message)

        accepted = 0
        for index, test_case in enumerate(test_cases, start=1):
            try:
                completed = subprocess.run(
                    command.run_command,
                    input=test_case.input_data,
                    text=True,
                    capture_output=True,
                    timeout=settings.judge_time_limit_seconds,
                    cwd=workdir,
                    env=_safe_env(),
                )
            except subprocess.TimeoutExpired:
                return JudgeResult("TLE", accepted * 100 // len(test_cases), _elapsed_ms(started), f"Time limit exceeded on case {index}.")

            if completed.returncode != 0:
                stderr = completed.stderr.strip() or "Program exited with non-zero status."
                return JudgeResult("RE", accepted * 100 // len(test_cases), _elapsed_ms(started), f"Runtime error on case {index}: {stderr[:500]}")

            actual = normalize_output(completed.stdout)
            expected = normalize_output(test_case.expected_output)
            if actual != expected:
                message = f"Wrong answer on case {index}. Expected: {expected[:200]!r}, got: {actual[:200]!r}"
                return JudgeResult("WA", accepted * 100 // len(test_cases), _elapsed_ms(started), message)

            accepted += 1

        return JudgeResult("AC", 100, _elapsed_ms(started), None)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@dataclass
class PreparedCommand:
    status: str
    run_command: list[str]
    error_message: str | None = None


def _prepare_command(language: str, code: str, workdir: Path) -> PreparedCommand:
    if language == "python":
        source = workdir / "main.py"
        source.write_text(code, encoding="utf-8")
        return PreparedCommand("READY", ["python", str(source)])

    if language == "cpp":
        source = workdir / "main.cpp"
        binary = workdir / "main.exe"
        source.write_text(code, encoding="utf-8")
        completed = subprocess.run(
            ["g++", "-std=c++17", "-O2", "-pipe", str(source), "-o", str(binary)],
            text=True,
            capture_output=True,
            timeout=20,
            cwd=workdir,
            env=_safe_env(),
        )
        if completed.returncode != 0:
            return PreparedCommand("CE", [], completed.stderr.strip()[:1000])
        return PreparedCommand("READY", [str(binary)])

    return PreparedCommand("CE", [], f"Unsupported language: {language}")


def _safe_env() -> dict[str, str]:
    allowed = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
    }
    if "PYTHONPATH" in os.environ:
        allowed["PYTHONPATH"] = os.environ["PYTHONPATH"]
    return allowed


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
