from rest_framework import serializers
from .models import ScriptTask, ScriptExecution
import json


class ScriptTaskSerializer(serializers.ModelSerializer):
    """脚本任务序列化器"""
    script_type_display = serializers.CharField(source='get_script_type_display', read_only=True)
    return_type_display = serializers.CharField(source='get_return_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    parameter_names = serializers.ListField(source='get_parameter_names', read_only=True)

    class Meta:
        model = ScriptTask
        fields = [
            'id', 'name', 'script_type', 'script_type_display',
            'return_type', 'return_type_display', 'parameters', 'parameter_names',
            'content', 'description', 'status', 'status_display', 'timeout',
            'last_executed_at', 'execution_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_executed_at', 'execution_count', 'created_at', 'updated_at']


class ScriptTaskCreateSerializer(serializers.ModelSerializer):
    """脚本任务创建序列化器"""

    class Meta:
        model = ScriptTask
        fields = [
            'name', 'script_type', 'return_type', 'parameters',
            'content', 'description', 'status', 'timeout'
        ]

    def validate_name(self, value):
        if ScriptTask.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError("脚本名称已存在")
        return value

    def validate_parameters(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("参数必须是有效的JSON对象")
        return value

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("脚本内容不能为空")
        return value


class ScriptExecutionSerializer(serializers.ModelSerializer):
    """脚本执行记录序列化器"""
    script_name = serializers.CharField(source='script_task.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ScriptExecution
        fields = [
            'id', 'script_task', 'script_name', 'status', 'status_display',
            'input_parameters', 'output', 'error_message', 'execution_time',
            'started_at', 'finished_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ScriptExecuteSerializer(serializers.Serializer):
    """脚本执行请求序列化器"""
    parameters = serializers.JSONField(
        required=False,
        default=dict,
        help_text="执行参数，JSON格式"
    )

    def validate_parameters(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("参数必须是有效的JSON对象")
        return value