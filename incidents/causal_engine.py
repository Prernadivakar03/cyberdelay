"""
CyberDelay: Causal Inference Engine
Damage Score Calculation & Counterfactual Analysis
"""

# Attack base severity weights (0-100 scale)
ATTACK_SEVERITY = {
    'ransomware': 90,
    'zero_day': 88,
    'insider_threat': 75,
    'mitm': 68,
    'sql_injection': 65,
    'ddos': 60,
    'phishing': 55,
    'brute_force': 45,
}

# Patch status multipliers
PATCH_MULTIPLIER = {
    'patched': 0.50,
    'partial': 0.75,
    'unpatched': 1.00,
}

# Firewall strength modifiers
FIREWALL_MODIFIER = {
    'strong': -15,
    'moderate': -7,
    'weak': 5,
    'none': 18,
}

# Data sensitivity multiplier
DATA_SENSITIVITY_MULT = {
    'public': 0.6,
    'internal': 0.8,
    'confidential': 1.0,
    'top_secret': 1.3,
}

# Attack vector modifier
ATTACK_VECTOR_MOD = {
    'external': 0,
    'internal': 8,
    'supply_chain': 12,
}

# Optimal detection threshold per attack type (minutes)
OPTIMAL_DETECTION = {
    'ransomware': 5,
    'zero_day': 8,
    'insider_threat': 30,
    'mitm': 10,
    'sql_injection': 12,
    'ddos': 3,
    'phishing': 20,
    'brute_force': 15,
}

# Counterfactual scenario — how much earlier (% of actual delay)
COUNTERFACTUAL_REDUCTION = 0.375  # simulate detection at 37.5% of actual delay


def calculate_damage_score(attack_type, detection_delay, server_load,
                            patch_status, firewall_status, affected_systems,
                            data_sensitivity='internal', attack_vector='external'):
    """
    Calculates a damage score (0–100) based on causal factors.

    Formula:
    Base = attack_severity × patch_multiplier
    Delay Impact = log-scaled delay contribution
    Load Impact = server load factor
    System Impact = log-scaled affected systems
    Modifiers = firewall + data sensitivity + attack vector

    Final = clamp(Base + all impacts + modifiers, 0, 100)
    """
    import math

    base_severity = ATTACK_SEVERITY.get(attack_type, 60)
    patch_mult = PATCH_MULTIPLIER.get(patch_status, 1.0)
    firewall_mod = FIREWALL_MODIFIER.get(firewall_status, 0)
    data_mult = DATA_SENSITIVITY_MULT.get(data_sensitivity, 1.0)
    vector_mod = ATTACK_VECTOR_MOD.get(attack_vector, 0)

    # Base damage from attack type and patch status
    base_damage = base_severity * patch_mult

    # Delay impact: logarithmic (early detection = big savings, late = diminishing)
    # Normalized: 0 delay = 0 extra damage, 120 min = ~25 extra damage
    delay_capped = min(detection_delay, 480)
    if delay_capped > 0:
        delay_impact = 18 * math.log(1 + delay_capped / 10)
    else:
        delay_impact = 0

    # Server load contribution (0-100 → 0-15 impact)
    load_impact = (server_load / 100) * 15

    # Affected systems (log scale: 1 system = 0, 100+ = ~12)
    systems_capped = max(affected_systems, 1)
    systems_impact = 8 * math.log10(systems_capped + 1)

    # Total raw score
    raw_score = base_damage + delay_impact + load_impact + systems_impact + firewall_mod + vector_mod

    # Apply data sensitivity multiplier
    raw_score = raw_score * data_mult

    # Clamp to 0–100
    final_score = max(0.0, min(100.0, raw_score))
    return round(final_score, 1)


def calculate_counterfactual(attack_type, detection_delay, server_load,
                              patch_status, firewall_status, affected_systems,
                              data_sensitivity='internal', attack_vector='external'):
    """
    Counterfactual: What if we detected the attack much earlier?
    Uses optimal detection threshold or 37.5% of actual delay (whichever is lower).
    Returns dict with counterfactual delay and damage.
    """
    optimal = OPTIMAL_DETECTION.get(attack_type, 10)
    reduced_delay = detection_delay * COUNTERFACTUAL_REDUCTION
    counterfactual_delay = max(min(reduced_delay, optimal), 1.0)

    counterfactual_damage = calculate_damage_score(
        attack_type, counterfactual_delay, server_load,
        patch_status, firewall_status, affected_systems,
        data_sensitivity, attack_vector
    )

    return {
        'counterfactual_delay': round(counterfactual_delay, 1),
        'counterfactual_damage': counterfactual_damage,
    }


def classify_risk(damage_score):
    """Maps damage score to risk level."""
    if damage_score < 30:
        return 'low'
    elif damage_score < 55:
        return 'medium'
    elif damage_score < 75:
        return 'high'
    else:
        return 'critical'


def get_risk_label(risk_level):
    labels = {
        'low': 'Low Risk',
        'medium': 'Medium Risk',
        'high': 'High Risk',
        'critical': 'Critical Risk',
    }
    return labels.get(risk_level, 'Unknown')


def get_recommendations(attack_type, damage_score, detection_delay, patch_status, firewall_status):
    """Generate actionable recommendations based on incident analysis."""
    recs = []

    optimal = OPTIMAL_DETECTION.get(attack_type, 10)
    if detection_delay > optimal * 2:
        recs.append({
            'icon': '⚡',
            'title': 'Improve Detection Speed',
            'detail': f'Target detection under {optimal} min for {attack_type.replace("_", " ").title()} attacks. '
                      f'Deploy SIEM/SOAR automation to cut response time.'
        })

    if patch_status == 'unpatched':
        recs.append({
            'icon': '🔧',
            'title': 'Urgent Patching Required',
            'detail': 'Unpatched systems significantly amplify attack damage. '
                      'Implement automated patch management immediately.'
        })
    elif patch_status == 'partial':
        recs.append({
            'icon': '🔧',
            'title': 'Complete Patch Coverage',
            'detail': 'Partial patching leaves critical vulnerabilities open. Complete all pending patches.'
        })

    if firewall_status in ('weak', 'none'):
        recs.append({
            'icon': '🛡️',
            'title': 'Upgrade Firewall Infrastructure',
            'detail': 'Weak/absent firewall multiplies attack surface. Upgrade to a Next-Gen Firewall with DPI.'
        })

    if damage_score >= 75:
        recs.append({
            'icon': '🚨',
            'title': 'Activate Incident Response Plan',
            'detail': 'Critical damage score detected. Immediately activate IR plan, isolate affected systems, '
                      'notify stakeholders, and engage forensic analysis.'
        })

    if attack_type in ('ransomware', 'zero_day'):
        recs.append({
            'icon': '💾',
            'title': 'Verify Offline Backups',
            'detail': f'{attack_type.replace("_", " ").title()} attacks often target backups. '
                      'Verify air-gapped offline backups are intact and recoverable.'
        })

    if not recs:
        recs.append({
            'icon': '✅',
            'title': 'Maintain Security Posture',
            'detail': 'Good detection time and defenses. Continue regular security audits and threat intelligence updates.'
        })

    return recs


def get_delay_damage_curve(attack_type, patch_status, firewall_status,
                            server_load=50, affected_systems=10,
                            data_sensitivity='internal', attack_vector='external'):
    """Generate delay vs damage curve data for Chart.js."""
    delays = [0, 5, 10, 15, 20, 30, 40, 60, 90, 120, 180, 240, 360, 480]
    data = []
    for d in delays:
        score = calculate_damage_score(
            attack_type, d, server_load, patch_status,
            firewall_status, affected_systems, data_sensitivity, attack_vector
        )
        data.append({'x': d, 'y': score})
    return data
