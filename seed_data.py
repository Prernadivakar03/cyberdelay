"""
seed_data.py — Populate CyberDelay database with sample incidents.
Run: python seed_data.py
"""
import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyberdelay.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from incidents.models import Incident
from incidents.causal_engine import (
    calculate_damage_score, calculate_counterfactual,
    classify_risk
)

random.seed(42)

SAMPLE_INCIDENTS = [
    # (attack_type, delay, server_load, patch_status, firewall_status, affected_systems, data_sens, vector)
    ('ransomware',    45, 85, 'unpatched',  'weak',     30, 'confidential', 'external'),
    ('ransomware',    10, 60, 'patched',    'strong',    5, 'internal',     'external'),
    ('ransomware',   120, 95, 'unpatched',  'none',     80, 'top_secret',   'external'),
    ('phishing',      20, 40, 'partial',   'moderate',  3, 'internal',     'external'),
    ('phishing',       5, 30, 'patched',   'strong',    1, 'public',       'external'),
    ('ddos',           3, 98, 'patched',   'moderate', 12, 'internal',     'external'),
    ('ddos',          15, 90, 'partial',   'weak',     25, 'public',       'external'),
    ('sql_injection', 30, 55, 'unpatched', 'weak',      8, 'confidential', 'external'),
    ('sql_injection',  8, 45, 'patched',   'strong',    2, 'internal',     'external'),
    ('zero_day',      60, 70, 'patched',   'strong',   15, 'top_secret',   'supply_chain'),
    ('zero_day',      90, 80, 'unpatched', 'none',     50, 'top_secret',   'supply_chain'),
    ('mitm',          25, 50, 'partial',   'moderate',  6, 'confidential', 'internal'),
    ('mitm',          40, 65, 'unpatched', 'weak',     10, 'internal',     'internal'),
    ('insider_threat',180, 30, 'patched',  'strong',   20, 'confidential', 'internal'),
    ('insider_threat', 60, 50, 'partial',  'moderate',  8, 'top_secret',   'internal'),
    ('brute_force',   15, 40, 'partial',   'moderate',  3, 'internal',     'external'),
    ('brute_force',    5, 35, 'patched',   'strong',    1, 'public',       'external'),
    ('ransomware',    75, 88, 'partial',   'weak',     40, 'confidential', 'supply_chain'),
    ('zero_day',      20, 75, 'partial',   'moderate', 12, 'confidential', 'external'),
    ('phishing',      35, 55, 'unpatched', 'none',      7, 'internal',     'external'),
]

print("Clearing existing incidents...")
Incident.objects.all().delete()

print(f"Seeding {len(SAMPLE_INCIDENTS)} sample incidents...")

for i, (attack_type, delay, load, patch, fw, systems, data_sens, vector) in enumerate(SAMPLE_INCIDENTS, 1):
    damage = calculate_damage_score(attack_type, delay, load, patch, fw, systems, data_sens, vector)
    cf = calculate_counterfactual(attack_type, delay, load, patch, fw, systems, data_sens, vector)
    risk = classify_risk(damage)
    damage_saved = round(damage - cf['counterfactual_damage'], 1)

    inc = Incident.objects.create(
        attack_type=attack_type,
        detection_delay=delay,
        server_load=load,
        patch_status=patch,
        firewall_status=fw,
        affected_systems=systems,
        data_sensitivity=data_sens,
        attack_vector=vector,
        damage_score=damage,
        counterfactual_delay=cf['counterfactual_delay'],
        counterfactual_damage=cf['counterfactual_damage'],
        damage_saved=damage_saved,
        risk_level=risk,
        notes=f'Sample incident #{i} — auto-generated seed data.',
    )
    print(f"  [{i:02d}] {attack_type:<18} delay={delay:>4}m  damage={damage:>5}  risk={risk}")

print(f"\n✓ Done! {Incident.objects.count()} incidents in database.")
print("  Open http://127.0.0.1:8000/ to see the dashboard.")
