from django.db import models
from common.models import BaseModel


class ProjectSpace(BaseModel):
    """项目空间模型"""
    name = models.CharField(
        max_length=100,
        verbose_name="项目名称",
        help_text="项目空间的名称"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="项目空间是否处于启用状态"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="项目描述"
    )

    class Meta:
        db_table = 'project_space'
        verbose_name = '项目空间'
        verbose_name_plural = '项目空间'

    def __str__(self):
        return self.name


class VehicleModel(BaseModel):
    """车型模型"""
    project_space = models.ForeignKey(
        ProjectSpace,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name="所属项目空间"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="车型名称"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="车型编码"
    )
    module = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="备用字段",
        help_text="原车型模块字段，现已由pipelines替代，保留作为备用"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="车型描述"
    )
    pipelines = models.JSONField(
        default=list,
        blank=True,
        verbose_name="管道配置",
        help_text="车型的管道配置信息"
    )

    class Meta:
        db_table = 'vehicle_model'
        verbose_name = '车型'
        verbose_name_plural = '车型'
        unique_together = ['project_space', 'code']  # 同一项目空间内车型编码唯一

    def __str__(self):
        return f"{self.project_space.name} - {self.name}"
        
    def get_pipeline_names(self):
        """获取所有管道名称"""
        if not self.pipelines:
            return []
        return [list(pipeline.keys())[0] for pipeline in self.pipelines if pipeline]
    
    def get_pipeline_data(self, pipeline_name):
        """获取指定管道的数据"""
        for pipeline in self.pipelines:
            if pipeline_name in pipeline:
                return pipeline[pipeline_name]
        return None