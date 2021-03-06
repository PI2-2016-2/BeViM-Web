from django.conf.urls import url
from bevim import views

urlpatterns = [

    url(r'^register$', views.HomeView.as_view(), name='register'),
    
    url(r'^how_to_use$', views.how_to_use, name='how_to_use'),

    url(r'^about$', views.about, name='about'),

    url(r'^new_experiment$', views.ExperimentView.as_view(),
        name='new_experiment'),

    url(r'^experiments$', views.ExperimentView().show_experiments,
        name='experiments'),

   	url(r'^experiment/(?P<experiment_id>\d+)$', views.ExperimentView().show_timer,
        name='timer'),

    url(r'^stop_experiment/(?P<experiment_id>\d+)$', views.ExperimentView().stop_experiment, name='stop_experiment'),

    url(r'^load_sensors$', views.ExperimentView().get_sensors, name='load_sensors'),

    url(r'^change_frequency$', views.change_frequency, name='change_frequency'),

    url(r'^consult_frequency$', views.consult_frequency, name='consult_frequency'),

    url(r'^receive_result$', views.ExperimentView().receive_result, name='receive_result'),
    
    url(r'^result/(?P<experiment_id>\d+)$', views.ExperimentView().experiment_result, name='experiment_result'),

    url(r'^result/(?P<experiment_id>\d+)/(?P<sensor_id>\d+)$', views.ExperimentView().experiment_result_by_sensor, name='experiment_result_by_sensor'),
    
    url(r'^processing_data/(?P<experiment_id>\d+)$', views.ExperimentView().process_result, name='process_result'),

]
