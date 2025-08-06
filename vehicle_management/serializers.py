from rest_framework import serializers
from .models import ProjectSpace, VehicleModel


class ProjectSpaceSerializer(serializers.ModelSerializer):
    """项目空间序列化器"""
    vehicle_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectSpace
        fields = ['id', 'name', 'is_active', 'description', 'created_at', 'updated_at', 'vehicle_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_vehicle_count(self, obj):
        """获取项目下车型数量"""
        return obj.vehicles.filter(is_deleted=False).count()


class ProjectSpaceCreateSerializer(serializers.ModelSerializer):
    """项目空间创建序列化器"""

    class Meta:
        model = ProjectSpace
        fields = ['name', 'is_active', 'description']

    def validate_name(self, value):
        if ProjectSpace.objects.filter(name=value, is_deleted=False).exists():
            raise serializers.ValidationError("项目名称已存在")
        return value


class VehicleModelSerializer(serializers.ModelSerializer):
    """车型序列化器"""
    project_space_name = serializers.CharField(source='project_space.name', read_only=True)

    class Meta:
        model = VehicleModel
        fields = ['id', 'project_space', 'project_space_name', 'name', 'code', 'module',
                  'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_code(self, value):
        # 创建时验证
        if self.instance is None:
            if VehicleModel.objects.filter(code=value, is_deleted=False).exists():
                raise serializers.ValidationError("车型编码已存在")
        # 更新时验证
        else:
            if VehicleModel.objects.filter(code=value, is_deleted=False).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("车型编码已存在")
        return value


class VehicleModelCreateSerializer(serializers.ModelSerializer):
    """车型创建序列化器"""

    class Meta:
        model = VehicleModel
        fields = ['project_space', 'name', 'code', 'module', 'description']