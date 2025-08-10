from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from .models import ProjectSpace, VehicleModel
from .serializers import (
    ProjectSpaceCreateSerializer,
    VehicleModelCreateSerializer
)


class ProjectSpaceService:
    """项目空间业务逻辑"""

    @staticmethod
    def get_all_projects(is_active=None, name=None):
        """获取所有项目空间，支持按状态和名称筛选"""
        queryset = ProjectSpace.objects.filter(is_deleted=False)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_project_by_id(project_id):
        """根据ID获取项目空间"""
        try:
            return ProjectSpace.objects.get(id=project_id, is_deleted=False)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_project(data):
        """创建项目空间"""
        serializer = ProjectSpaceCreateSerializer(data=data)
        if serializer.is_valid():
            project = serializer.save()
            return project, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def update_project(project_id, data):
        """更新项目空间"""
        project = ProjectSpaceService.get_project_by_id(project_id)
        if not project:
            return None, "项目不存在"

        serializer = ProjectSpaceCreateSerializer(project, data=data, partial=True)
        if serializer.is_valid():
            updated_project = serializer.save()
            return updated_project, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def delete_project(project_id):
        """删除项目空间（软删除）"""
        project = ProjectSpaceService.get_project_by_id(project_id)
        if not project:
            return False, "项目不存在"

        # 检查是否有关联的车型
        if project.vehicles.filter(is_deleted=False).exists():
            return False, "该项目下还有车型，无法删除"

        project.is_deleted = True
        project.save()
        return True, "删除成功"


class VehicleModelService:
    """车型业务逻辑"""

    @staticmethod
    def get_vehicles_by_project(project_id, code=None, name=None):
        """根据项目ID获取车型列表，支持按名称和编码筛选"""
        queryset = VehicleModel.objects.filter(
            project_space_id=project_id,
            is_deleted=False
        )
        if name:
            queryset = queryset.filter(name__icontains=name)
        if code:
            queryset = queryset.filter(code__icontains=code)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_all_vehicles(name=None, code=None):
        """获取所有车型，支持按名称和编码筛选"""
        queryset = VehicleModel.objects.filter(is_deleted=False)
        if name:
            queryset = queryset.filter(name__icontains=name)
        if code:
            queryset = queryset.filter(code__icontains=code)
        return queryset.order_by('-created_at')

    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        """根据ID获取车型"""
        try:
            return VehicleModel.objects.get(id=vehicle_id, is_deleted=False)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_vehicle(data):
        """创建车型"""
        serializer = VehicleModelCreateSerializer(data=data)
        if serializer.is_valid():
            # 验证项目空间是否存在且启用
            project_space = ProjectSpaceService.get_project_by_id(data.get('project_space'))
            if not project_space:
                return None, "项目空间不存在"
            if not project_space.is_active:
                return None, "项目空间未启用，无法添加车型"

            vehicle = serializer.save()
            return vehicle, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def update_vehicle(vehicle_id, data):
        """更新车型"""
        vehicle = VehicleModelService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return None, "车型不存在"
            
        # 如果传入了project_space参数，验证项目空间是否存在且启用
        if 'project_space' in data:
            project_space = ProjectSpaceService.get_project_by_id(data.get('project_space'))
            if not project_space:
                return None, "项目空间不存在"
            if not project_space.is_active:
                return None, "项目空间未启用，无法修改车型所属项目"

        serializer = VehicleModelCreateSerializer(vehicle, data=data, partial=True)
        if serializer.is_valid():
            updated_vehicle = serializer.save()
            return updated_vehicle, None
        return None, serializer.errors

    @staticmethod
    @transaction.atomic
    def delete_vehicle(vehicle_id):
        """删除车型（软删除）"""
        vehicle = VehicleModelService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False, "车型不存在"

        vehicle.is_deleted = True
        vehicle.save()
        return True, "删除成功"