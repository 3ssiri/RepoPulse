import json
from pathlib import PurePosixPath

from repopulse.models import FileItem


def find_file(files: list[FileItem], names: set[str]) -> FileItem | None:
    lower_names = {name.lower() for name in names}
    for file in files:
        if file.type == "blob" and PurePosixPath(file.path).name.lower() in lower_names:
            return file
    return None


def has_path_prefix(files: list[FileItem], prefixes: tuple[str, ...]) -> bool:
    return any(file.path.lower().startswith(prefix.lower()) for file in files for prefix in prefixes)


def parse_json_content(content: str | None) -> dict:
    if not content:
        return {}
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
