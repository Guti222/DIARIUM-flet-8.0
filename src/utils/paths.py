import os
import sys
import tempfile

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(os.getcwd())
    return os.path.join(base_path, relative_path)

def get_db_path(db_name: str = "libro_facil.db", app_folder: str = "Librofacil") -> str:
    """Return a writable, persistent path for the SQLite DB.

    - On Windows: prefers %LOCALAPPDATA%/Librofacil or %APPDATA%/Librofacil
    - On other OS: ~/.librofacil
    - Falls back to a writable current directory if needed
    """

    def _is_writable_dir(path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            test_file = os.path.join(path, ".write_test")
            with open(test_file, "w", encoding="utf-8") as fh:
                fh.write("ok")
            os.remove(test_file)
            return True
        except Exception:
            return False

    candidates: list[str] = []
    if os.name == "nt":
        for env_var in ("LOCALAPPDATA", "APPDATA", "USERPROFILE"):
            base = os.getenv(env_var)
            if base:
                candidates.append(os.path.join(base, app_folder))
    else:
        home = os.path.expanduser("~")
        if home:
            candidates.append(os.path.join(home, f".{app_folder.lower()}"))

    # Siempre incluir cwd al final (puede no ser escribible en ejecutable)
    candidates.append(os.path.join(os.getcwd(), app_folder))

    folder = None
    for candidate in candidates:
        if _is_writable_dir(candidate):
            folder = candidate
            break

    if not folder:
        folder = os.getcwd()

    return os.path.join(folder, db_name)
