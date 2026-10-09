"""
PostgreSQL Setup & Connection Helper for SaaS Business Analytics Platform.
Run this script anytime to configure and test your PostgreSQL database:
    python setup_postgres.py
"""

import sys
import psycopg

def configure_postgresql():
    print("=" * 60)
    print(" SaaS Business Analytics Platform - PostgreSQL Setup")
    print("=" * 60)
    
    host = input("PostgreSQL Host [localhost]: ").strip() or "localhost"
    port = input("PostgreSQL Port [5432]: ").strip() or "5432"
    user = input("PostgreSQL User [postgres]: ").strip() or "postgres"
    password = input("PostgreSQL Password: ").strip()
    db_name = input("Database Name [saas_analytics]: ").strip() or "saas_analytics"
    
    print("\n[+] Testing connection to PostgreSQL server...")
    try:
        # Connect to default postgres database first to create the target db if needed
        conn = psycopg.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port,
            autocommit=True
        )
        print("[✓] Successfully connected to PostgreSQL server!")
        
        # Check if database exists
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cur.fetchone()
            if not exists:
                print(f"[+] Database '{db_name}' does not exist. Creating it now...")
                cur.execute(f'CREATE DATABASE "{db_name}"')
                print(f"[✓] Database '{db_name}' created successfully!")
            else:
                print(f"[✓] Database '{db_name}' already exists.")
        conn.close()
        
        # Write .env file
        env_content = f"""DEBUG=True
SECRET_KEY=saas-analytics-secret-key-super-secure-change-in-prod-2026
DB_ENGINE=postgresql
DB_NAME={db_name}
DB_USER={user}
DB_PASSWORD={password}
DB_HOST={host}
DB_PORT={port}
"""
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print(f"[✓] Updated .env file with PostgreSQL configuration.")
        print("\n[+] Running Django migrations on PostgreSQL...")
        import subprocess
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("\n[🎉] PostgreSQL setup is complete and ready to use!")
        
    except Exception as e:
        print(f"\n[!] Failed to connect to PostgreSQL: {e}")
        print("Please verify your PostgreSQL password and try again.")

if __name__ == "__main__":
    configure_postgresql()

