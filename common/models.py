from django.db import models
import uuid


class BaseModel(models.Model):
    """基础模型，包含公共字段"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="主键ID"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="是否删除"
    )

    class Meta:
        abstract = True  # 抽象模型，不会创建数据表
        ordering = ['-created_at']