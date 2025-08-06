# Django DevUI Template

## 1. 核心设计理念

- 分层架构：Model层 → Service层 → View层 → API层
- 前后端分离：Django作为API服务，Vue3作为前端
- 统一响应格式：标准化的成功/失败/分页响应
- 代码复用：BaseModel基础模型，公共组件封装

## 2. 项目结构

```
project/
├── common/                 # 公共模块
│   ├── __init__.py
│   ├── models.py          # BaseModel基础模型
│   ├── responses.py       # 统一响应格式
│   ├── exceptions.py      # 自定义异常
│   └── pagination.py      # 分页组件
├── vehicle_management/    # 业务应用
│   ├── __init__.py
│   ├── models.py          # 数据模型层
│   ├── serializers.py     # 序列化层(Schema)
│   ├── services.py        # 业务逻辑层
│   ├── views.py           # 控制器层
│   ├── urls.py            # 路由配置
│   └── admin.py
├── admin_core/           # 项目配置
│   ├── __init__.py
│   ├── settings.py       # 项目配置
│   ├── urls.py           # 主路由
│   └── wsgi.py
├── requirements.txt      # 依赖包
└── manage.py
```

## 3. 新增子模块开发流程

### 3.1 创建新的应用

```bash
# 在项目根目录执行
python manage.py startapp new_module_name
```

### 3.2 注册应用到settings

```python
# admin_core/settings.py
INSTALLED_APPS = [
    # ... 其他应用
    'new_module_name',  # 添加新应用
]
```

### 3.3 创建模型层

```python
# new_module_name/models.py
from common.models import BaseModel
from django.db import models

class YourModel(BaseModel):  # 继承BaseModel，自动获得id、时间戳、软删除字段
    name = models.CharField(max_length=100, verbose_name="名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    status = models.BooleanField(default=True, verbose_name="状态")
    
    class Meta:
        db_table = 'your_table_name'
        verbose_name = '你的模型'
        verbose_name_plural = '你的模型'
    
    def __str__(self):
        return self.name
```

### 3.4 创建序列化层

```python
# new_module_name/serializers.py
from rest_framework import serializers
from .models import YourModel

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = ['id', 'name', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class YourModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = ['name', 'description', 'status']
    
    def validate_name(self, value):
        if YourModel.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError("名称已存在")
        return value
```

### 3.5 创建业务逻辑层

```python
# new_module_name/services.py
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import YourModel
from .serializers import YourModelSerializer, YourModelCreateSerializer

class YourModelService:
    @staticmethod
    def get_all_items(status=None):
        """获取所有数据"""
        queryset = YourModel.objects.filter(is_deleted=False)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_item_by_id(item_id):
        """根据ID获取数据"""
        try:
            return YourModel.objects.get(id=item_id, is_deleted=False)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_item(data):
        """创建数据"""
        serializer = YourModelCreateSerializer(data=data)
        if serializer.is_valid():
            item = serializer.save()
            return item, None
        return None, serializer.errors
    
    @staticmethod
    @transaction.atomic
    def update_item(item_id, data):
        """更新数据"""
        item = YourModelService.get_item_by_id(item_id)
        if not item:
            return None, "数据不存在"
        
        serializer = YourModelCreateSerializer(item, data=data, partial=True)
        if serializer.is_valid():
            updated_item = serializer.save()
            return updated_item, None
        return None, serializer.errors
    
    @staticmethod
    @transaction.atomic
    def delete_item(item_id):
        """删除数据（软删除）"""
        item = YourModelService.get_item_by_id(item_id)
        if not item:
            return False, "数据不存在"
        
        item.is_deleted = True
        item.save()
        return True, "删除成功"
```

### 3.6 创建视图控制器

```python
# new_module_name/views.py
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from common.responses import ApiResponse
from .services import YourModelService
from .serializers import YourModelSerializer

class YourModelView(APIView):
    @swagger_auto_schema(
        operation_summary="获取数据列表",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="状态筛选", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('page', openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER),
        ],
        responses={200: YourModelSerializer(many=True)}
    )
    def get(self, request):
        """获取数据列表"""
        status = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        if status is not None:
            status = status.lower() == 'true'
        
        queryset = YourModelService.get_all_items(status=status)
        
        return ApiResponse.paginated_response(
            queryset=queryset,
            page=page,
            page_size=page_size,
            serializer_class=YourModelSerializer,
            request=request
        )
    
    @swagger_auto_schema(
        operation_summary="创建数据",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='名称'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='描述'),
                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='状态'),
            },
            required=['name']
        ),
        responses={200: YourModelSerializer()}
    )
    def post(self, request):
        """创建数据"""
        item, errors = YourModelService.create_item(request.data)
        if item:
            serializer = YourModelSerializer(item)
            return ApiResponse.success(data=serializer.data, message="创建成功")
        return ApiResponse.error(message="创建失败", data=errors)

class YourModelDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="获取数据详情",
        responses={200: YourModelSerializer()}
    )
    def get(self, request, item_id):
        """获取数据详情"""
        item = YourModelService.get_item_by_id(item_id)
        if not item:
            return ApiResponse.error(message="数据不存在", code=404)
        
        serializer = YourModelSerializer(item)
        return ApiResponse.success(data=serializer.data)
    
    @swagger_auto_schema(
        operation_summary="更新数据",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='名称'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='描述'),
                'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='状态'),
            }
        ),
        responses={200: YourModelSerializer()}
    )
    def put(self, request, item_id):
        """更新数据"""
        item, errors = YourModelService.update_item(item_id, request.data)
        if item:
            serializer = YourModelSerializer(item)
            return ApiResponse.success(data=serializer.data, message="更新成功")
        return ApiResponse.error(message=errors if isinstance(errors, str) else "更新失败", data=errors)
    
    @swagger_auto_schema(
        operation_summary="删除数据",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT)}
    )
    def delete(self, request, item_id):
        """删除数据"""
        success, message = YourModelService.delete_item(item_id)
        if success:
            return ApiResponse.success(message=message)
        return ApiResponse.error(message=message)
```

### 3.7 配置路由

```python
# new_module_name/urls.py
from django.urls import path
from .views import YourModelView, YourModelDetailView

app_name = 'new_module_name'

urlpatterns = [
    path('items/', YourModelView.as_view(), name='item-list'),
    path('items/<uuid:item_id>/', YourModelDetailView.as_view(), name='item-detail'),
]
```

### 3.8 添加到主路由

```python
# admin_core/urls.py
urlpatterns = [
    # ... 其他路由
    path('api/v1/', include('apps.new_module_name.urls')),
]
```

### 3.9 执行数据库迁移

```bash
python manage.py makemigrations new_module_name
python manage.py migrate
```

