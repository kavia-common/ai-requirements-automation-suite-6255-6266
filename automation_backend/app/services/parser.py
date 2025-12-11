import os
import csv
from typing import List, Dict, Tuple

try:
    import pandas as pd  # optional but preferred
except Exception:  # pragma: no cover
    pd = None


def _normalize_header(header: str) -> str:
    return header.strip().lower().replace(" ", "_")


# PUBLIC_INTERFACE
def parse_requirements(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    PUBLIC_INTERFACE
    Parse requirements from CSV or Excel into normalized dicts.
    Expected columns (best effort): title, description, priority, component, tags.

    Returns:
        (requirements, warnings)
    """
    ext = os.path.splitext(file_path)[1].lower()
    warnings: List[str] = []
    rows: List[Dict] = []

    if ext in [".csv"]:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({k: v for k, v in r.items()})
    elif ext in [".xls", ".xlsx"]:
        if pd is None:
            warnings.append("pandas not installed, attempting simplistic CSV-like read failed for Excel.")
            raise ValueError("Excel parsing requires pandas. Install pandas or provide CSV.")
        df = pd.read_excel(file_path)
        rows = df.to_dict(orient="records")
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    norm_reqs: List[Dict] = []
    for r in rows:
        r_norm = {(_normalize_header(k)): ("" if v is None else str(v)) for k, v in r.items()}
        title = r_norm.get("title") or r_norm.get("requirement") or r_norm.get("name")
        description = r_norm.get("description") or r_norm.get("details") or ""
        priority = r_norm.get("priority") or ""
        component = r_norm.get("component") or r_norm.get("module") or ""
        tags = r_norm.get("tags") or ""
        if not title:
            warnings.append("Row missing a 'title' or equivalent; skipped.")
            continue
        norm_reqs.append(
            {
                "title": title.strip(),
                "description": description.strip(),
                "priority": priority.strip(),
                "component": component.strip(),
                "tags": tags.strip(),
            }
        )

    return norm_reqs, warnings
