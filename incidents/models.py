from django.db import models

ATTACK_TYPES = [
    ('ransomware', 'Ransomware'),
    ('phishing', 'Phishing'),
    ('ddos', 'DDoS Attack'),
    ('sql_injection', 'SQL Injection'),
    ('mitm', 'Man-in-the-Middle'),
    ('zero_day', 'Zero-Day Exploit'),
    ('insider_threat', 'Insider Threat'),
    ('brute_force', 'Brute Force'),
]

PATCH_STATUS = [
    ('patched', 'Fully Patched'),
    ('partial', 'Partially Patched'),
    ('unpatched', 'Unpatched'),
]

FIREWALL_STATUS = [
    ('strong', 'Strong (Next-Gen Firewall)'),
    ('moderate', 'Moderate (Standard Firewall)'),
    ('weak', 'Weak (Basic/Outdated)'),
    ('none', 'No Firewall'),
]

RISK_LEVELS = [
    ('low', 'Low Risk'),
    ('medium', 'Medium Risk'),
    ('high', 'High Risk'),
    ('critical', 'Critical Risk'),
]


class Incident(models.Model):
    # Attack Details
    attack_type = models.CharField(max_length=50, choices=ATTACK_TYPES)
    detection_delay = models.FloatField(help_text="Detection delay in minutes")
    server_load = models.FloatField(help_text="Server load at time of attack (0–100%)")
    patch_status = models.CharField(max_length=20, choices=PATCH_STATUS)
    firewall_status = models.CharField(max_length=20, choices=FIREWALL_STATUS)
    affected_systems = models.IntegerField(help_text="Number of systems affected")
    data_sensitivity = models.CharField(
        max_length=20,
        choices=[('public', 'Public'), ('internal', 'Internal'), ('confidential', 'Confidential'), ('top_secret', 'Top Secret')],
        default='internal'
    )
    attack_vector = models.CharField(
        max_length=20,
        choices=[('external', 'External'), ('internal', 'Internal'), ('supply_chain', 'Supply Chain')],
        default='external'
    )
    notes = models.TextField(blank=True, null=True)

    # Computed Fields
    damage_score = models.FloatField(null=True, blank=True)
    counterfactual_damage = models.FloatField(null=True, blank=True)
    counterfactual_delay = models.FloatField(null=True, blank=True)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, blank=True)
    damage_saved = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_attack_type_display()} | Delay: {self.detection_delay}min | Damage: {self.damage_score}"
