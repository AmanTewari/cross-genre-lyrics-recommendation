import subprocess
import sys
from argparse import ArgumentParser


steps = [
    "pipeline/run_step1.py",
    "pipeline/run_step2.py",
    "pipeline/run_step3.py",
    "pipeline/run_step4.py",
]


def _resolve_skips(skip_values: list[str]) -> set[str]:
    alias_to_step = {
        "1": "pipeline/run_step1.py",
        "2": "pipeline/run_step2.py",
        "3": "pipeline/run_step3.py",
        "4": "pipeline/run_step4.py",
        "step1": "pipeline/run_step1.py",
        "step2": "pipeline/run_step2.py",
        "step3": "pipeline/run_step3.py",
        "step4": "pipeline/run_step4.py",
        "run_step1.py": "pipeline/run_step1.py",
        "run_step2.py": "pipeline/run_step2.py",
        "run_step3.py": "pipeline/run_step3.py",
        "run_step4.py": "pipeline/run_step4.py",
    }
    resolved: set[str] = set()
    for value in skip_values:
        key = value.strip().lower()
        if key in alias_to_step:
            resolved.add(alias_to_step[key])
        else:
            raise SystemExit(
                f"Invalid --skip value: {value}. Use step1..step4, 1..4, or run_stepN.py."
            )
    return resolved


def run(skip_values: list[str] | None = None) -> None:
    skip_steps = _resolve_skips(skip_values or [])

    for step in steps:
        if step in skip_steps:
            print(f"\nSKIPPED: {step}\n")
            continue

        print(f"\nRUNNING: {step}\n")

        result = subprocess.run([sys.executable, step])

        if result.returncode != 0:
            print(f"FAILED at {step}")
            raise SystemExit(1)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    parser = ArgumentParser(description="Run the lyrics pipeline step-by-step.")
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Steps to skip (e.g. step2 run_step3.py 4)",
    )
    args = parser.parse_args()
    run(skip_values=args.skip)
