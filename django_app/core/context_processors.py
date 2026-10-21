from core.translations import get_all_translations
from accounts.permissions import get_user_role
from patients.models import Patient


def localization_context(request):
    """
    Context processor injecting active language, translation dict,
    and role information to all templates.
    """
    # Active language priority: Session -> User profile -> Default 'en'
    lang = request.session.get('django_language')
    if not lang and request.user.is_authenticated and hasattr(request.user, 'profile'):
        lang = request.user.profile.preferred_language
    if not lang or lang not in ['en', 'hi', 'mr']:
        lang = 'en'

    translations = get_all_translations(lang)
    role = get_user_role(request.user) if request.user.is_authenticated else None

    patient_record = None
    if request.user.is_authenticated:
        try:
            patient_record = Patient.objects.filter(user=request.user).first()
        except Exception:
            patient_record = None

    return {
        'CURRENT_LANG': lang,
        't': translations,
        'user_role': role,
        'user_patient': patient_record,
    }
