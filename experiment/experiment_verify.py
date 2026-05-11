import csv
import subprocess
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
proof_runs_dir = repo_root / "experiment" / "proof_runs"
output_csv = repo_root / "experiment" / "proof_verification.csv"
verifier = repo_root / "experiment" / "helve"

run_dirs = []
for task_file in proof_runs_dir.rglob("task.txt"):
    run_dir = task_file.parent
    if (run_dir / "proof.txt").exists():
        run_dirs.append(run_dir)
run_dirs.sort()

rows = []
total = len(run_dirs)
row_count = 0
for run_dir in run_dirs:
    print("[" + str(row_count + 1) + "/" + str(total) + "] Verifying", run_dir)

    task_file = run_dir / "task.txt"
    proof_file = run_dir / "proof.txt"
    completed = subprocess.run(
        [
            str(verifier),
            "verify",
            str(task_file),
            str(proof_file),
            "--timeout=30",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    stdout_last = completed.stdout.strip().splitlines()
    stderr_last = completed.stderr.strip().splitlines()
    is_valid = completed.returncode == 0

    rows.append(
        {
            "run_dir": str(run_dir),
            "task_file": str(task_file),
            "proof_file": str(proof_file),
            "status": "valid" if is_valid else "invalid",
            "is_valid": int(is_valid),
            "returncode": completed.returncode,
            "stdout_last_line": stdout_last[-1] if stdout_last else "",
            "stderr_last_line": stderr_last[-1] if stderr_last else "",
        }
    )
    row_count += 1

output_csv.parent.mkdir(parents=True, exist_ok=True)
with output_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "run_dir",
            "task_file",
            "proof_file",
            "status",
            "is_valid",
            "returncode",
            "stdout_last_line",
            "stderr_last_line",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

valid = 0
for row in rows:
    valid += row["is_valid"]
invalid = len(rows) - valid
print("Wrote", len(rows), "rows to", output_csv)
print("Valid:", valid)
print("Invalid:", invalid)