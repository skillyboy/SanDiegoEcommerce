"""
Simple database wait helper used in Docker entrypoint.
It uses psycopg2 to attempt connections to Postgres using DATABASE_URL
or PG* environment variables. Retries for a configurable timeout.
"""
import os
import time
import urllib.parse

try:
    import psycopg2
except Exception:
    psycopg2 = None


def wait_for_postgres(timeout: int = 30, interval: float = 1.0):
    if psycopg2 is None:
        print("psycopg2 not installed; skipping DB wait")
        return True

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Parse database_url with urllib
        try:
            parsed = urllib.parse.urlparse(database_url)
            dbname = parsed.path.lstrip('/')
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
        except Exception:
            print("Invalid DATABASE_URL; skipping wait")
            return False
    else:
        host = os.getenv('PGHOST')
        dbname = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB')
        user = os.getenv('PGUSER') or os.getenv('POSTGRES_USER')
        password = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD')
        port = int(os.getenv('PGPORT') or os.getenv('POSTGRES_PORT') or 5432)

    start = time.time()
    while True:
        try:
            conn = psycopg2.connect(host=host, dbname=dbname, user=user, password=password, port=port)
            conn.close()
            print(f"Database reachable at {host}:{port}/{dbname}")
            return True
        except Exception as e:
            elapsed = time.time() - start
            if elapsed > timeout:
                print(f"Timed out waiting for database ({elapsed}s): {e}")
                return False
            print(f"Waiting for database at {host}:{port}... ({int(elapsed)}s elapsed)")
            time.sleep(interval)


if __name__ == '__main__':
    ok = wait_for_postgres(int(os.getenv('DB_WAIT_TIMEOUT', '30')))
    if not ok:
        raise SystemExit(1)
