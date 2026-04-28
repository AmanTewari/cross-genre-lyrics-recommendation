import subprocess
import sys


steps = [
    "run_step1.py",
    "run_step2.py",
    "run_step3.py",
    "run_step4.py",
]


def run() -> None:
    for step in steps:
        print(f"\nRUNNING: {step}\n")

        result = subprocess.run([sys.executable, step])

        if result.returncode != 0:
            print(f"FAILED at {step}")
            raise SystemExit(1)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run()
