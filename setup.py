#!/usr/bin/env python3
"""
setup.py — One-click setup for CyberDelay project.
Run: python setup.py
"""
import subprocess
import sys
import os

def run(cmd, desc):
    print(f"\n>>> {desc}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"    ✗ Failed. Check error above.")
        sys.exit(1)
    print(f"    ✓ Done")

print("=" * 55)
print("  CyberDelay — Project Setup")
print("=" * 55)

# 1. Install dependencies
run(f"{sys.executable} -m pip install django pandas", "Installing Django and pandas")

# 2. Make migrations
run(f"{sys.executable} manage.py makemigrations incidents", "Creating database migrations")
run(f"{sys.executable} manage.py migrate", "Applying migrations")

# 3. Create superuser non-interactively
os.environ['DJANGO_SUPERUSER_PASSWORD'] = 'admin123'
run(
    f"{sys.executable} manage.py createsuperuser --noinput --username admin --email admin@cyberdelay.local",
    "Creating admin user (admin / admin123)"
)

# 4. Seed data
run(f"{sys.executable} seed_data.py", "Seeding sample incident data")

print("\n" + "=" * 55)
print("  ✓ Setup complete!")
print("=" * 55)
print()
print("  Start the server:")
print(f"    python manage.py runserver")
print()
print("  Then open:")
print("    http://127.0.0.1:8000/         → App")
print("    http://127.0.0.1:8000/admin/   → Admin (admin / admin123)")
print()
