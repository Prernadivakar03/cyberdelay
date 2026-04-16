from django import forms
from .models import Incident, ATTACK_TYPES, PATCH_STATUS, FIREWALL_STATUS


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = [
            'attack_type', 'detection_delay', 'server_load',
            'patch_status', 'firewall_status', 'affected_systems',
            'data_sensitivity', 'attack_vector', 'notes'
        ]
        widgets = {
            'attack_type': forms.Select(attrs={'class': 'form-select'}),
            'detection_delay': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 45', 'min': '0', 'max': '1440', 'step': '0.5'
            }),
            'server_load': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 75', 'min': '0', 'max': '100', 'step': '0.1'
            }),
            'patch_status': forms.Select(attrs={'class': 'form-select'}),
            'firewall_status': forms.Select(attrs={'class': 'form-select'}),
            'affected_systems': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 12', 'min': '1'
            }),
            'data_sensitivity': forms.Select(attrs={'class': 'form-select'}),
            'attack_vector': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes about this incident...'
            }),
        }
        labels = {
            'attack_type': 'Attack Type',
            'detection_delay': 'Detection Delay (minutes)',
            'server_load': 'Server Load at Attack Time (%)',
            'patch_status': 'System Patch Status',
            'firewall_status': 'Firewall Strength',
            'affected_systems': 'Number of Affected Systems',
            'data_sensitivity': 'Data Sensitivity Level',
            'attack_vector': 'Attack Vector',
            'notes': 'Additional Notes',
        }

    def clean_detection_delay(self):
        val = self.cleaned_data.get('detection_delay')
        if val is not None and val < 0:
            raise forms.ValidationError("Detection delay cannot be negative.")
        return val

    def clean_server_load(self):
        val = self.cleaned_data.get('server_load')
        if val is not None and (val < 0 or val > 100):
            raise forms.ValidationError("Server load must be between 0 and 100.")
        return val

    def clean_affected_systems(self):
        val = self.cleaned_data.get('affected_systems')
        if val is not None and val < 1:
            raise forms.ValidationError("At least 1 system must be affected.")
        return val
