from django.urls import path
from .views import login_view, logout_view, register_view, job_query_view, home

urlpatterns = [
    path('', login_view, name='login'),  # Redirect to login page as the root URL
    path('home/', home, name='home'),  # Home page after login
    path('logout/', logout_view, name='logout'),  # Logout page
    path('register/', register_view, name='register'),  # Registration page
    path('job_query/', job_query_view, name='job_query'),  # Job query submission
]
