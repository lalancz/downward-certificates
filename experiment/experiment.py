import csv
import shutil
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
benchmarks_dir = repo_root / "misc" / "tests" / "benchmarks"
runs_dir = repo_root / "experiment" / "proof_runs"
output_csv = repo_root / "experiment" / "proof_sizes.csv"

tasks = []
for path in benchmarks_dir.rglob("*.pddl"):
    name = path.name.lower()
    if name == "domain.pddl" or name.startswith("domain_") or name.startswith("domain-") or name.endswith("-domain.pddl"):
        continue
    tasks.append(path)
tasks.sort()

if runs_dir.exists():
    shutil.rmtree(runs_dir)
runs_dir.mkdir(parents=True, exist_ok=True)
output_csv.parent.mkdir(parents=True, exist_ok=True)

searches = [
    (
        "lmcut",
        'astar(lmcut(), unsolv_verification=proof, certificate_directory="{cert_dir}")',
    ),
    (
        "merge_and_shrink",
        'astar(merge_and_shrink(merge_strategy=merge_precomputed(merge_tree=linear()), shrink_strategy=shrink_bisimulation(), label_reduction=exact(before_shrinking=true,before_merging=false), prune_unreachable_states=false), unsolv_verification=proof, certificate_directory="{cert_dir}")',
    ),
]

with output_csv.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "task",
            "lmcut_proof_size_bytes",
            "merge_and_shrink_proof_size_bytes",
        ],
    )
    writer.writeheader()

    row_count = 0
    for task in tasks:
        rel_task = task.relative_to(repo_root)
        safe_name = str(rel_task.with_suffix("")).replace("\\", "__").replace("/", "__")
        print("Running", rel_task)

        row = {"task": str(rel_task)}
        for name, search_template in searches:
            cert_dir = runs_dir / (safe_name + "__" + name)
            cert_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                sys.executable,
                str(repo_root / "fast-downward.py"),
                "--overall-time-limit",
                "60s",
                str(task),
                "--search",
                search_template.format(cert_dir=cert_dir.as_posix()),
            ]
            subprocess.run(cmd, cwd=repo_root, check=False)

            proof_path = cert_dir / "proof.txt"
            if proof_path.exists():
                row[name + "_proof_size_bytes"] = str(proof_path.stat().st_size)
            else:
                row[name + "_proof_size_bytes"] = ""

        writer.writerow(row)
        row_count += 1

print("Wrote", row_count, "rows to", output_csv)