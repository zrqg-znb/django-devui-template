from django.db import models
from common.models import BaseModel, ExecutableModel
import json


class ScriptTask(ExecutableModel):
    """自定义脚本任务模型"""

    SCRIPT_TYPE_CHOICES = [
        ('bash', 'Bash脚本'),
        ('python', 'Python脚本'),
    ]

    RETURN_TYPE_CHOICES = [
        ('text', '纯文本'),
        ('json', 'JSON格式'),
        ('html', 'HTML格式'),
        ('xml', 'XML格式'),
    ]

    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '禁用'),
        ('draft', '草稿'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="脚本名称",
        help_text="脚本任务的名称"
    )
    script_type = models.CharField(
        max_length=10,
        choices=SCRIPT_TYPE_CHOICES,
        default='bash',
        verbose_name="脚本类型"
    )
    return_type = models.CharField(
        max_length=10,
        choices=RETURN_TYPE_CHOICES,
        default='text',
        verbose_name="返回类型"
    )
    parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="脚本参数",
        help_text="JSON格式的参数定义"
    )
    content = models.TextField(
        verbose_name="脚本内容",
        help_text="脚本的具体内容"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="备注说明"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="状态"
    )
    timeout = models.PositiveIntegerField(
        default=300,
        verbose_name="超时时间(秒)",
        help_text="脚本执行超时时间，默认5分钟"
    )

    class Meta:
        db_table = 'script_task'
        verbose_name = '脚本任务'
        verbose_name_plural = '脚本任务'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['script_type']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_script_type_display()})"

    def get_parameter_names(self):
        """获取参数名称列表"""
        if isinstance(self.parameters, dict):
            return list(self.parameters.keys())
        return []


class ScriptExecution(BaseModel):
    """脚本执行记录模型"""

    STATUS_CHOICES = [
        ('running', '执行中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('timeout', '超时'),
        ('cancelled', '已取消'),
    ]

    script_task = models.ForeignKey(
        ScriptTask,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name="关联脚本"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='running',
        verbose_name="执行状态"
    )
    input_parameters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="输入参数"
    )
    output = models.TextField(
        blank=True,
        null=True,
        verbose_name="执行输出"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="错误信息"
    )
    execution_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="执行耗时(秒)"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="开始时间"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="结束时间"
    )

    class Meta:
        db_table = 'script_execution'
        verbose_name = '脚本执行记录'
        verbose_name_plural = '脚本执行记录'
        indexes = [
            models.Index(fields=['script_task', '-started_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.script_task.name} - {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_formatted_output(self):
        """获取格式化的输出信息"""
        if not self.output:
            return "无输出"
        return self.output
    
    def has_output(self):
        """检查是否有输出内容"""
        return bool(self.output and self.output.strip())
    
    def get_execution_summary(self):
        """获取执行摘要信息"""
        summary = {
            'status': self.get_status_display(),
            'execution_time': f"{self.execution_time:.2f}秒" if self.execution_time else "未知",
            'has_output': self.has_output(),
            'has_error': bool(self.error_message),
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S'),
            'finished_at': self.finished_at.strftime('%Y-%m-%d %H:%M:%S') if self.finished_at else "未完成"
        }
        return summary