import os
import sys

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.getcwd())
    return os.path.join(base_path, relative_path)

def get_db_path(db_name: str = "libro_facil.db", app_folder: str = "Librofacil") -> str:
    """Return a writable, persistent path for the SQLite DB.

    - On Windows: %LOCALAPPDATA%/Librofacil/libro_facil.db (creates folder)
    - On other OS: ~/.librofacil/libro_facil.db (creates folder)
    - Falls back to current working directory if env var missing.
    """
    if os.name == "nt":
        base = os.getenv("LOCALAPPDATA") or os.getcwd()
        folder = os.path.join(base, app_folder)
    else:
        home = os.path.expanduser("~")
        folder = os.path.join(home, f".{app_folder.lower()}")
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = os.getcwd()
    return os.path.join(folder, db_name)
