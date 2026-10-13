from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_project_file(body):
    """Read one project text file without invoking a shell or following escapes."""
    path = (ROOT / body.strip()).resolve()
    relative = path.relative_to(ROOT)
    if any(part.startswith('.') for part in relative.parts):
        raise PermissionError('Hidden files and directories are excluded.')
    if not path.is_file():
        raise ValueError('Provide a relative project file path.')
    with path.open(encoding='utf-8') as stream:
        return stream.read(16000)
