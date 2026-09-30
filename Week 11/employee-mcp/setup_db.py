"""Starts a Postgres Docker container and loads the schema + simulated data.

Usage:  python setup_db.py
Re-running wipes the container and recreates everything (handy in class).
"""
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psycopg

from config import CONTAINER_NAME, DB_CONFIG

DB_DIR = Path(__file__).parent / "db"


def sh(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def start_container() -> None:
    if shutil.which("docker") is None:
        sys.exit("Docker not found. Install Docker Desktop / Engine first.")
    print(f"Recreating container '{CONTAINER_NAME}' ...")
    sh(["docker", "rm", "-f", CONTAINER_NAME], check=False)
    sh([
        "docker", "run", "-d",
        "--name", CONTAINER_NAME,
        "-e", f"POSTGRES_USER={DB_CONFIG['user']}",
        "-e", f"POSTGRES_PASSWORD={DB_CONFIG['password']}",
        "-e", f"POSTGRES_DB={DB_CONFIG['dbname']}",
        "-p", f"{DB_CONFIG['port']}:5432",
        "postgres:16",
    ])


def wait_for_db(timeout: int = 60) -> psycopg.Connection:
    print("Waiting for Postgres to accept connections ", end="", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            conn = psycopg.connect(**DB_CONFIG)
            print(" ready.")
            return conn
        except psycopg.OperationalError:
            print(".", end="", flush=True)
            time.sleep(1)
    sys.exit("\nTimed out waiting for Postgres.")


def main() -> None:
    start_container()
    with wait_for_db() as conn:
        for name in ("schema.sql", "seed.sql"):
            print(f"Applying {name} ...")
            conn.execute((DB_DIR / name).read_text())
        conn.commit()
        for table in ("departments", "employees", "salaries", "work_assignments"):
            count = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            print(f"  {table:<18} {count} rows")
    print("\nDone. Database is ready on "
          f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")


if __name__ == "__main__":
    main()
