from django.urls import path
from .views import (
    ProjectSpaceView, ProjectSpaceDetailView,
    VehicleModelView, VehicleModelDetailView
)

app_name = 'vehicle_management'

urlpatterns = [
    # 项目空间相关
    path('projects/', ProjectSpaceView.as_view(), name='project-list'),
    path('projects/<uuid:project_id>/', ProjectSpaceDetailView.as_view(), name='project-detail'),

    # 车型相关
    path('vehicles/', VehicleModelView.as_view(), name='vehicle-list'),
    path('vehicles/<uuid:vehicle_id>/', VehicleModelDetailView.as_view(), name='vehicle-detail'),
]