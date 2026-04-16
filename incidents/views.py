import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Incident
from .forms import IncidentForm
from .causal_engine import (
    calculate_damage_score, calculate_counterfactual,
    classify_risk, get_risk_label, get_recommendations,
    get_delay_damage_curve, ATTACK_SEVERITY, OPTIMAL_DETECTION
)


def home(request):
    """Home page with project overview and stats."""
    total = Incident.objects.count()
    critical = Incident.objects.filter(risk_level='critical').count()
    avg_damage = Incident.objects.aggregate(avg=Avg('damage_score'))['avg']
    avg_delay = Incident.objects.aggregate(avg=Avg('detection_delay'))['avg']
    recent = Incident.objects.all()[:5]

    context = {
        'total_incidents': total,
        'critical_count': critical,
        'avg_damage': round(avg_damage, 1) if avg_damage else 0,
        'avg_delay': round(avg_delay, 1) if avg_delay else 0,
        'recent_incidents': recent,
    }
    return render(request, 'incidents/home.html', context)


def submit_incident(request):
    """Incident entry form."""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)

            # Calculate damage score
            incident.damage_score = calculate_damage_score(
                incident.attack_type,
                incident.detection_delay,
                incident.server_load,
                incident.patch_status,
                incident.firewall_status,
                incident.affected_systems,
                incident.data_sensitivity,
                incident.attack_vector,
            )

            # Calculate counterfactual
            cf = calculate_counterfactual(
                incident.attack_type,
                incident.detection_delay,
                incident.server_load,
                incident.patch_status,
                incident.firewall_status,
                incident.affected_systems,
                incident.data_sensitivity,
                incident.attack_vector,
            )
            incident.counterfactual_delay = cf['counterfactual_delay']
            incident.counterfactual_damage = cf['counterfactual_damage']
            incident.damage_saved = round(incident.damage_score - cf['counterfactual_damage'], 1)

            # Classify risk
            incident.risk_level = classify_risk(incident.damage_score)

            incident.save()
            messages.success(request, 'Incident submitted and analyzed successfully.')
            return redirect('incident_result', pk=incident.pk)
    else:
        form = IncidentForm()

    return render(request, 'incidents/submit.html', {'form': form})


def incident_result(request, pk):
    """Full analysis result page for a single incident."""
    incident = get_object_or_404(Incident, pk=pk)

    recommendations = get_recommendations(
        incident.attack_type,
        incident.damage_score,
        incident.detection_delay,
        incident.patch_status,
        incident.firewall_status,
    )

    # Delay vs Damage curve for this incident's parameters
    curve_data = get_delay_damage_curve(
        incident.attack_type,
        incident.patch_status,
        incident.firewall_status,
        incident.server_load,
        incident.affected_systems,
        incident.data_sensitivity,
        incident.attack_vector,
    )

    # Causal insight
    optimal_delay = OPTIMAL_DETECTION.get(incident.attack_type, 10)
    time_saved = round(incident.detection_delay - incident.counterfactual_delay, 1)

    risk_colors = {
        'low': '#22c55e',
        'medium': '#f59e0b',
        'high': '#f97316',
        'critical': '#ef4444',
    }

    context = {
        'incident': incident,
        'recommendations': recommendations,
        'curve_data': json.dumps(curve_data),
        'optimal_delay': optimal_delay,
        'time_saved': time_saved,
        'risk_color': risk_colors.get(incident.risk_level, '#6b7280'),
        'risk_label': get_risk_label(incident.risk_level),
        'damage_pct_saved': round((incident.damage_saved / incident.damage_score * 100), 1) if incident.damage_score > 0 else 0,
    }
    return render(request, 'incidents/result.html', context)


def incident_history(request):
    """All incidents table with filtering."""
    incidents = Incident.objects.all()

    # Filters
    attack_filter = request.GET.get('attack_type', '')
    risk_filter = request.GET.get('risk_level', '')

    if attack_filter:
        incidents = incidents.filter(attack_type=attack_filter)
    if risk_filter:
        incidents = incidents.filter(risk_level=risk_filter)

    from .models import ATTACK_TYPES, RISK_LEVELS
    context = {
        'incidents': incidents,
        'attack_types': ATTACK_TYPES,
        'risk_levels': RISK_LEVELS,
        'attack_filter': attack_filter,
        'risk_filter': risk_filter,
        'total': incidents.count(),
    }
    return render(request, 'incidents/history.html', context)


def dashboard(request):
    """Dashboard with all charts."""
    incidents = Incident.objects.all()

    if incidents.count() == 0:
        return render(request, 'incidents/dashboard.html', {'no_data': True})

    # Delay vs Damage scatter data
    scatter_data = list(incidents.values('detection_delay', 'damage_score', 'attack_type', 'risk_level'))

    # Attack type frequency
    attack_counts = (
        incidents.values('attack_type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    attack_labels = [a['attack_type'].replace('_', ' ').title() for a in attack_counts]
    attack_values = [a['count'] for a in attack_counts]

    # Risk distribution
    risk_dist = (
        incidents.values('risk_level')
        .annotate(count=Count('id'))
        .order_by('risk_level')
    )
    risk_order = ['low', 'medium', 'high', 'critical']
    risk_dict = {r['risk_level']: r['count'] for r in risk_dist}
    risk_labels = ['Low', 'Medium', 'High', 'Critical']
    risk_values = [risk_dict.get(k, 0) for k in risk_order]

    # Average damage per attack type
    avg_damage_by_type = (
        incidents.values('attack_type')
        .annotate(avg_dmg=Avg('damage_score'))
        .order_by('-avg_dmg')
    )
    avg_labels = [a['attack_type'].replace('_', ' ').title() for a in avg_damage_by_type]
    avg_values = [round(a['avg_dmg'], 1) for a in avg_damage_by_type]

    # Damage saved summary
    total_saved = sum(i.damage_saved for i in incidents if i.damage_saved)
    avg_delay_all = incidents.aggregate(avg=Avg('detection_delay'))['avg']
    avg_damage_all = incidents.aggregate(avg=Avg('damage_score'))['avg']

    # Timeline (recent 20 incidents)
    timeline = list(
        incidents.order_by('created_at')[:20].values(
            'created_at', 'damage_score', 'counterfactual_damage', 'detection_delay'
        )
    )
    timeline_labels = [t['created_at'].strftime('%d %b %H:%M') for t in timeline]
    timeline_actual = [t['damage_score'] for t in timeline]
    timeline_cf = [t['counterfactual_damage'] for t in timeline]

    context = {
        'no_data': False,
        'scatter_data': json.dumps(scatter_data),
        'attack_labels': json.dumps(attack_labels),
        'attack_values': json.dumps(attack_values),
        'risk_labels': json.dumps(risk_labels),
        'risk_values': json.dumps(risk_values),
        'avg_labels': json.dumps(avg_labels),
        'avg_values': json.dumps(avg_values),
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_actual': json.dumps(timeline_actual),
        'timeline_cf': json.dumps(timeline_cf),
        'total_incidents': incidents.count(),
        'avg_delay': round(avg_delay_all, 1) if avg_delay_all else 0,
        'avg_damage': round(avg_damage_all, 1) if avg_damage_all else 0,
        'total_saved': round(total_saved, 1),
        'critical_count': incidents.filter(risk_level='critical').count(),
    }
    return render(request, 'incidents/dashboard.html', context)


def delete_incident(request, pk):
    """Delete an incident."""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        incident.delete()
        messages.success(request, 'Incident deleted.')
    return redirect('history')
