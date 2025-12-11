import os
from typing import Dict, List, Tuple

# Simple rule templates for fallback generation
RULE_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "login": {
        "test_name": "test_login_flow",
        "steps": [
            "Navigate to login page",
            "Enter valid username and password",
            "Click login",
            "Assert user is redirected to dashboard",
        ],
    },
    "search": {
        "test_name": "test_search_functionality",
        "steps": [
            "Navigate to search page",
            "Enter query text",
            "Submit search",
            "Assert results are displayed",
        ],
    },
}


def _infer_rule_key(req: Dict) -> str:
    title = (req.get("title") or "").lower()
    description = (req.get("description") or "").lower()
    for key in RULE_TEMPLATES.keys():
        if key in title or key in description:
            return key
    return "generic"


def _generic_template(req: Dict) -> Dict:
    title = (req.get("title") or "case")
    safe = title.lower().replace(" ", "_")[:40]
    return {
        "test_name": f"test_{safe}",
        "steps": [
            f"Context: {(req.get('component') or '').strip()}",
            f"Requirement: {(req.get('title') or '').strip()}",
            "Open application",
            "Perform relevant actions based on requirement description",
            "Verify expected outcomes",
        ],
    }


# PUBLIC_INTERFACE
def generate_testcases_and_code(requirements: List[Dict], base_dir: str) -> Tuple[List[Dict], List[str]]:
    """
    PUBLIC_INTERFACE
    Generate:
      - testcase JSON-like descriptions
      - simple pytest test modules organized under base_dir/tests

    Returns:
      (testcase_specs, script_paths)
    """
    testcases: List[Dict] = []
    paths: List[str] = []
    tests_root = os.path.join(base_dir, "tests")
    os.makedirs(tests_root, exist_ok=True)

    for req in requirements:
        key = _infer_rule_key(req)
        tpl = RULE_TEMPLATES.get(key) or _generic_template(req)
        test_name = tpl["test_name"]
        steps = tpl["steps"]
        testcases.append({"name": test_name, "steps": steps, "requirement": req})

        module_name = f"test_{test_name}.py"
        module_path = os.path.join(tests_root, module_name)
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(_emit_pytest_module(test_name, steps))
        paths.append(module_path)

    # basic conftest to configure base-url
    conftest_path = os.path.join(tests_root, "conftest.py")
    if not os.path.exists(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(_emit_conftest())

    return testcases, paths


def _emit_pytest_module(test_name: str, steps: List[str]) -> str:
    # Build a plain string to avoid complex f-string nesting that can cause lint parse issues
    header = "import os\n\n"
    def_line = f"def {test_name}():\n"
    doc = "    \"\"\"\n    Auto-generated test case.\n    \"\"\"\n"
    step_lines = ""
    for s in steps:
        step_lines += f"    # Step: {s}\n"
    end = "    assert True\n"
    return header + def_line + doc + step_lines + end


def _emit_conftest() -> str:
    # Simple conftest with --base-url option
    return (
        "import os\n"
        "import pytest\n\n"
        "def pytest_addoption(parser):\n"
        '    parser.addoption("--base-url", action="store", default=os.getenv("BASE_URL", "http://localhost:3000"))\n\n'
        "@pytest.fixture\n"
        "def base_url(request):\n"
        '    return request.config.getoption("--base-url")\n'
    )
