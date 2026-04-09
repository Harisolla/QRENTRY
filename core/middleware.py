# middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class RoleRedirectMiddleware:
    """
    Redirect users to choose-role page if their profile role is not set,
    but skip admin, logout, static, media, and the choose-role page itself.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ask_role = request.session.get('ask_role', False)
            
            # Paths to exclude from redirection
            excluded_paths = [
                reverse('choose_role'),
                reverse('admin:index'),
                reverse('account_logout'),  # if using allauth logout
            ]
            
            # Add static and media paths
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                excluded_paths.append(request.path)
            
            if ask_role and request.path not in excluded_paths:
                return redirect('choose_role')

        response = self.get_response(request)
        return response
