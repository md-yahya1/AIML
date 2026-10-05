
import subprocess

def git_status():

    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return f"Git error: {result.stderr}"

    return result.stdout.strip()