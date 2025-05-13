import os
from alembic.config import Config
from alembic.script import ScriptDirectory

alembic_cfg = Config("migrations/alembic.ini")
script = ScriptDirectory.from_config(alembic_cfg)

heads = script.get_heads()

version_files = [
    f for f in os.listdir("migrations/versions")
    if f.endswith(".py") and not f.startswith("__")
]
known_versions = [f.split("_")[0] for f in version_files]

missing = set(heads) - set(known_versions)

if missing:
    print("ERROR: Migration file missing for Alembic revision(s):", ", ".join(missing))
    exit(1)
else:
    print("Alembic migration check passed.")
