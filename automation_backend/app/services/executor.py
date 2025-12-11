import os
import shutil
import subprocess
from typing import Tuple


# PUBLIC_INTERFACE
def run_pytests_with_allure(tests_dir: str, allure_results_dir: str, allure_report_dir: str, timeout: int = 600, extra_args: str = "") -> Tuple[int, str, str]:
    """
    PUBLIC_INTERFACE
    Execute pytest for the specified tests_dir and collect Allure results.

    Returns:
      (returncode, stdout, stderr)
    """
    os.makedirs(allure_results_dir, exist_ok=True)
    os.makedirs(allure_report_dir, exist_ok=True)

    # Clean previous results
    for d in [allure_results_dir, allure_report_dir]:
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if os.path.isfile(p):
                os.remove(p)
            else:
                shutil.rmtree(p, ignore_errors=True)

    cmd = [
        "pytest",
        tests_dir,
        f"--alluredir={allure_results_dir}",
        "-q",
    ]
    if extra_args:
        cmd.extend(extra_args.split(" "))

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    # Try generating allure static report if allure tool available
    try:
        subprocess.run(
            ["allure", "generate", allure_results_dir, "-o", allure_report_dir, "--clean"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception:
        # Allure CLI not available; report folder will remain empty, but results exist
        pass

    return proc.returncode, stdout, stderr
