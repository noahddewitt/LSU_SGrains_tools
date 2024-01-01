"""sg_db URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="sg_db/index_info.html"), name = "index_info"), #Allows loading template directly without views file
    path("crossing_shiny", TemplateView.as_view(template_name="sg_db/crossing_shiny.html"), name = "crossing_shiny"), 
    path('crossing/', include("crossing.urls")),
    path('tools/', include("tools.urls")),
    path('germplasm/', include("germplasm.urls")),
    path('admin/', admin.site.urls),
]
