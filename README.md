<<<<<<< HEAD
# cyberdelay
CyberDelay is a data-driven web application that measures how delays in detecting cyberattacks increase organizational damage. It models the relationship between detection time and impact using simulations and causal analysis. By enabling “what-if” scenarios, it helps organizations understand losses and improve early threat detection strategies.
=======
# CyberDelay
### Cyberattack Detection Delay Impact Analysis Using Causal Inference

A full Django web application that quantifies how detection delay amplifies
cyberattack damage — and computes counterfactual "what-if" scenarios to show
how much damage could have been prevented.

---

## Quick Start (3 commands)

```bash
cd cyberdelay
python setup.py          # installs deps, migrates DB, seeds data, creates admin
python manage.py runserver
```

Then open **http://127.0.0.1:8000/**

Admin panel: http://127.0.0.1:8000/admin/ → `admin` / `admin123`

Live Demo: https://cyberdelay.onrender.com/

---

## Manual Setup (if setup.py fails)

```bash
# 1. Install dependencies
pip install django pandas

# 2. Database
python manage.py makemigrations incidents
python manage.py migrate

# 3. Admin user
python manage.py createsuperuser

# 4. (Optional) Load sample data
python seed_data.py

# 5. Run
python manage.py runserver
```

---

## Project Structure

```
cyberdelay/
├── manage.py
├── setup.py               ← one-click setup
├── seed_data.py           ← sample incident loader
├── requirements.txt
├── db.sqlite3             ← auto-created on first migrate
│
├── cyberdelay/            ← Django project config
│   ├── settings.py
│   └── urls.py
│
├── incidents/             ← main app
│   ├── models.py          ← Incident model
│   ├── views.py           ← all page logic
│   ├── forms.py           ← incident entry form
│   ├── causal_engine.py   ← damage calculation + counterfactual logic
│   ├── admin.py
│   └── templates/
│       └── incidents/
│           ├── home.html
│           ├── submit.html
│           ├── result.html
│           ├── history.html
│           └── dashboard.html
│
└── templates/
    └── base.html          ← shared layout/navbar
```

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Home — overview, stats, recent incidents |
| `/submit/` | Log new incident with live score preview |
| `/result/<id>/` | Full analysis: damage, causal comparison, recommendations |
| `/history/` | All incidents table with filters |
| `/dashboard/` | Charts: scatter, pie, bar, timeline |
| `/admin/` | Django admin panel |

---

## Damage Score Formula

```
Base      = attack_severity × patch_multiplier
DelayImp  = 18 × log(1 + delay/10)        ← log-scaled: biggest impact early
LoadImp   = (server_load/100) × 15
SysImp    = 8 × log10(affected_systems+1)
FwMod     = firewall modifier (-15 to +18)
VectorMod = attack vector modifier (0 to +12)

RawScore  = (Base + DelayImp + LoadImp + SysImp + FwMod + VectorMod)
            × data_sensitivity_multiplier

FinalScore = clamp(RawScore, 0, 100)
```

## Counterfactual (Causal Inference)

The app simulates: *"What if this attack was detected 62.5% earlier?"*

```
counterfactual_delay  = min(actual_delay × 0.375, optimal_detection_threshold)
counterfactual_damage = calculate_damage_score(counterfactual_delay, ...)
damage_saved          = actual_damage - counterfactual_damage
```

## Risk Classification

| Score | Level |
|-------|-------|
| 0–29 | Low |
| 30–54 | Medium |
| 55–74 | High |
| 75–100 | Critical |

---

## Tech Stack

- **Backend:** Django 4.2, Python 3.10+
- **Database:** SQLite (zero config)
- **Frontend:** Bootstrap 5.3, JetBrains Mono font, Syne font
- **Charts:** Chart.js 4.4
- **Icons:** Bootstrap Icons
- **Data:** pandas (available for CSV import extension)
>>>>>>> 5524afa (Initial commit - ready for deployment)
