from accounts.models import Manager

def get_manager_for_user(user):
    """
    Get or create a manager profile for a user.
    """
    if user.is_superuser:
        # For superuser, get the first manager or create one
        manager = Manager.objects.first()
        if not manager:
            manager = Manager.objects.create(
                user=user,
                department='Administration',
                phone_number='0000000000'
            )
        return manager
    
    # Try to get dashboard_manager first
    try:
        return user.dashboard_manager
    except:
        # Try to get account_manager
        try:
            return user.account_manager
        except Manager.DoesNotExist:
            return None 