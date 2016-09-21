from django.conf.urls import url
from bevim import views

urlpatterns = [

    url(r'^register$', views.HomeView.as_view(), name='register'),

    url(r'^new_experiment$', views.ExperimentView.as_view(),
        name='new_experiment'),

    url(r'^experiments$', views.ExperimentView.as_view(),
        name='experiments'),
]
