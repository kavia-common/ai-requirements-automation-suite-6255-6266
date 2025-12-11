import os
import json
from typing import Any


def save_uploaded_file(file_storage, dest_folder: str) -> str:
    """
    Save an uploaded FileStorage to the destination folder and return the path.
    """
    os.makedirs(dest_folder, exist_ok=True)
    filename = file_storage.filename
    path = os.path.join(dest_folder, filename)
    file_storage.save(path)
    return path


def write_json(data: Any, path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path
