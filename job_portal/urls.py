from django.contrib import admin
from django.urls import path, include
from job.views import home  # Import the home view

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel URL
    path('', home, name='home'),      # Root URL mapped to the home view
    path('job/', include('job.urls')),  # Include URLs from the job app
]
