from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import ScriptTask, ScriptExecution
from .serializers import (
    ScriptTaskSerializer, ScriptTaskCreateSerializer,
    ScriptExecutionSerializer, ScriptExecuteSerializer
)
from .script_executor import ScriptExecutor
import threading
import logging

logger = logging.getLogger(__name__)


class ScriptTaskService:
    """脚本任务业务逻辑"""

    @staticmethod
    def get_all_scripts(status=None, script_type=None):
        """获取所有脚本任务"""
        queryset = ScriptTask.objects.filter(is_deleted=False)
        if status:
            queryset = queryset.filter(status=status)
        if script_type:
            queryset = queryset.filter(script_type=script_type)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_script_by_id(script_id):
        """根据ID获取脚本任务"""
        try:
            return ScriptTask.objects.get(id=script_id, is_deleted=False)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_script(data):
        """创建脚本任务"""
        serializer = ScriptTaskCreateSerializer(data=data)
        if serializer.is_valid():
            script = serializer.save()
            return script, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def update_script(script_id, data):
        """更新脚本任务"""
        script = ScriptTaskService.get_script_by_id(script_id)
        if not script:
            return None, "脚本不存在"

        serializer = ScriptTaskCreateSerializer(script, data=data, partial=True)
        if serializer.is_valid():
            updated_script = serializer.save()
            return updated_script, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def delete_script(script_id):
        """删除脚本任务"""
        script = ScriptTaskService.get_script_by_id(script_id)
        if not script:
            return False, "脚本不存在"

        # 检查是否有正在执行的任务
        running_executions = script.executions.filter(status='running')
        if running_executions.exists():
            return False, "脚本正在执行中，无法删除"

        script.is_deleted = True
        script.save()
        return True, "删除成功"

    @staticmethod
    def execute_script(script_id, parameters=None):
        """执行脚本任务"""
        script = ScriptTaskService.get_script_by_id(script_id)
        if not script:
            return None, "脚本不存在"

        if script.status != 'active':
            return None, "脚本未启用，无法执行"

        # 验证参数
        serializer = ScriptExecuteSerializer(data={'parameters': parameters or {}})
        if not serializer.is_valid():
            return None, serializer.errors

        # 创建执行记录
        execution = ScriptExecution.objects.create(
            script_task=script,
            status='running',
            input_parameters=parameters or {}
        )

        # 异步执行脚本
        thread = threading.Thread(
            target=ScriptTaskService._execute_script_async,
            args=(script, execution)
        )
        thread.daemon = True
        thread.start()

        return execution, None

    @staticmethod
    def _execute_script_async(script, execution):
        """异步执行脚本"""
        try:
            executor = ScriptExecutor(script)
            success, output, error, exec_time = executor.execute(execution.input_parameters)

            # 更新执行记录
            execution.status = 'success' if success else 'failed'
            execution.output = output
            execution.error_message = error
            execution.execution_time = exec_time
            execution.finished_at = timezone.now()
            execution.save()

            # 更新脚本任务统计
            script.last_executed_at = timezone.now()
            script.execution_count += 1
            script.save()

        except Exception as e:
            logger.error(f"脚本执行异常: {e}")
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.finished_at = timezone.now()
            execution.save()


class ScriptExecutionService:
    """脚本执行记录业务逻辑"""

    @staticmethod
    def get_executions_by_script(script_id):
        """获取脚本的执行记录"""
        return ScriptExecution.objects.filter(
            script_task_id=script_id,
            script_task__is_deleted=False
        ).order_by('-started_at')

    @staticmethod
    def get_all_executions():
        """获取所有执行记录"""
        return ScriptExecution.objects.filter(
            script_task__is_deleted=False
        ).select_related('script_task').order_by('-started_at')

    @staticmethod
    def get_execution_by_id(execution_id):
        """根据ID获取执行记录"""
        try:
            return ScriptExecution.objects.get(id=execution_id)
        except ObjectDoesNotExist:
            return None