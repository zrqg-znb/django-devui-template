from django.urls import path
from .views import (
    ScriptTaskView, ScriptTaskDetailView, ScriptExecuteView,
    ScriptExecutionView, ScriptExecutionDetailView
)

app_name = 'system'

urlpatterns = [
    # 脚本任务相关
    path('scripts/', ScriptTaskView.as_view(), name='script-list'),
    path('scripts/<uuid:script_id>/', ScriptTaskDetailView.as_view(), name='script-detail'),
    path('scripts/<uuid:script_id>/execute/', ScriptExecuteView.as_view(), name='script-execute'),

    # 脚本执行记录相关
    path('executions/', ScriptExecutionView.as_view(), name='execution-list'),
    path('executions/<uuid:execution_id>/', ScriptExecutionDetailView.as_view(), name='execution-detail'),
]