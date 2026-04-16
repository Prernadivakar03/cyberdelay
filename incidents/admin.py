from django.contrib import admin
from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['id', 'attack_type', 'detection_delay', 'damage_score', 'risk_level', 'created_at']
    list_filter = ['attack_type', 'risk_level', 'patch_status', 'firewall_status']
    search_fields = ['attack_type', 'notes']
    readonly_fields = ['damage_score', 'counterfactual_damage', 'counterfactual_delay', 'damage_saved', 'risk_level', 'created_at']
    ordering = ['-created_at']
