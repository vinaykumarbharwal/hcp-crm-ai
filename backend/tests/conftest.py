import os
from pathlib import Path

TEST_DB = Path(__file__).resolve().parent / "test_hcp_crm.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["GROQ_API_KEY"] = ""