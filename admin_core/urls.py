from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger配置
schema_view = get_schema_view(
    openapi.Info(
        title="Django API",
        default_version='v1',
        description="Django管理系统的API文档",
        contact=openapi.Contact(email="zrqznb020528@gamil.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/v1/', include('vehicle_management.urls')),
    path('api/v1/system/', include('system.urls')),
    # Swagger文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]