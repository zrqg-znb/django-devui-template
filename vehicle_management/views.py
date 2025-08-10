from rest_framework.views import APIView
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from common.responses import ApiResponse
from .services import ProjectSpaceService, VehicleModelService
from .serializers import ProjectSpaceSerializer, VehicleModelSerializer


class ProjectSpaceView(APIView):
    """项目空间视图"""

    @swagger_auto_schema(
        operation_summary="获取项目空间列表",
        operation_description="获取所有项目空间，支持按状态和名称筛选，以及分页",
        manual_parameters=[
            openapi.Parameter('is_active', openapi.IN_QUERY, description="是否启用", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('name', openapi.IN_QUERY, description="项目名称（模糊匹配）", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ProjectSpaceSerializer(many=True)}
    )
    def get(self, request):
        """获取项目空间列表"""
        is_active = request.query_params.get('is_active')
        name = request.query_params.get('name')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        # 处理is_active参数
        if is_active is not None:
            is_active = is_active.lower() == 'true'

        queryset = ProjectSpaceService.get_all_projects(is_active=is_active, name=name)

        return ApiResponse.paginated_response(
            queryset=queryset,
            page=page,
            page_size=page_size,
            serializer_class=ProjectSpaceSerializer,
            request=request
        )

    @swagger_auto_schema(
        operation_summary="创建项目空间",
        operation_description="创建新的项目空间",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否启用'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='项目描述'),
            },
            required=['name']
        ),
        responses={200: ProjectSpaceSerializer()}
    )
    def post(self, request):
        """创建项目空间"""
        project, errors = ProjectSpaceService.create_project(request.data)
        if project:
            serializer = ProjectSpaceSerializer(project)
            return ApiResponse.success(data=serializer.data, message="项目创建成功")
        return ApiResponse.error(message="创建失败", data=errors)


class ProjectSpaceDetailView(APIView):
    """项目空间详情视图"""

    @swagger_auto_schema(
        operation_summary="获取项目空间详情",
        operation_description="根据ID获取项目空间详情",
        responses={200: ProjectSpaceSerializer()}
    )
    def get(self, request, project_id):
        """获取项目空间详情"""
        project = ProjectSpaceService.get_project_by_id(project_id)
        if not project:
            return ApiResponse.error(message="项目不存在", code=404)

        serializer = ProjectSpaceSerializer(project)
        return ApiResponse.success(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="更新项目空间",
        operation_description="根据ID更新项目空间信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否启用'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='项目描述'),
            }
        ),
        responses={200: ProjectSpaceSerializer()}
    )
    def put(self, request, project_id):
        """更新项目空间"""
        project, errors = ProjectSpaceService.update_project(project_id, request.data)
        if project:
            serializer = ProjectSpaceSerializer(project)
            return ApiResponse.success(data=serializer.data, message="更新成功")
        return ApiResponse.error(message=errors if isinstance(errors, str) else "更新失败", data=errors)

    @swagger_auto_schema(
        operation_summary="删除项目空间",
        operation_description="根据ID删除项目空间（软删除）",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT)}
    )
    def delete(self, request, project_id):
        """删除项目空间"""
        success, message = ProjectSpaceService.delete_project(project_id)
        if success:
            return ApiResponse.success(message=message)
        return ApiResponse.error(message=message)


class VehicleModelView(APIView):
    """车型视图"""

    @swagger_auto_schema(
        operation_summary="获取车型列表",
        operation_description="获取车型列表，可按项目空间、名称和编码筛选",
        manual_parameters=[
            openapi.Parameter('project_id', openapi.IN_QUERY, description="项目空间ID", type=openapi.TYPE_STRING),
            openapi.Parameter('name', openapi.IN_QUERY, description="车型名称（模糊匹配）", type=openapi.TYPE_STRING),
            openapi.Parameter('code', openapi.IN_QUERY, description="车型编码（模糊匹配）", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER),
        ],
        responses={200: VehicleModelSerializer(many=True)}
    )
    def get(self, request):
        """获取车型列表"""
        project_id = request.query_params.get('project_id')
        name = request.query_params.get('name')
        code = request.query_params.get('code')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        if project_id:
            queryset = VehicleModelService.get_vehicles_by_project(project_id, code=code, name=name)
        else:
            queryset = VehicleModelService.get_all_vehicles(name=name, code=code)

        return ApiResponse.paginated_response(
            queryset=queryset,
            page=page,
            page_size=page_size,
            serializer_class=VehicleModelSerializer,
            request=request
        )

    @swagger_auto_schema(
        operation_summary="创建车型",
        operation_description="创建新的车型",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_space': openapi.Schema(type=openapi.TYPE_STRING, description='项目空间ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='车型名称'),
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='车型编码'),
                'module': openapi.Schema(type=openapi.TYPE_STRING, description='车型模块'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='车型描述'),
            },
            required=['project_space', 'name', 'code', 'module']
        ),
        responses={200: VehicleModelSerializer()}
    )
    def post(self, request):
        """创建车型"""
        vehicle, errors = VehicleModelService.create_vehicle(request.data)
        if vehicle:
            serializer = VehicleModelSerializer(vehicle)
            return ApiResponse.success(data=serializer.data, message="车型创建成功")
        return ApiResponse.error(message="创建失败", data=errors)


class VehicleModelDetailView(APIView):
    """车型详情视图"""

    @swagger_auto_schema(
        operation_summary="获取车型详情",
        operation_description="根据ID获取车型详情",
        responses={200: VehicleModelSerializer()}
    )
    def get(self, request, vehicle_id):
        """获取车型详情"""
        vehicle = VehicleModelService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return ApiResponse.error(message="车型不存在", code=404)

        serializer = VehicleModelSerializer(vehicle)
        return ApiResponse.success(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="更新车型",
        operation_description="根据ID更新车型信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'project_space': openapi.Schema(type=openapi.TYPE_STRING, description='所属项目空间ID'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='车型名称'),
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='车型编码'),
                'module': openapi.Schema(type=openapi.TYPE_STRING, description='车型模块'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='车型描述'),
            }
        ),
        responses={200: VehicleModelSerializer()}
    )
    def put(self, request, vehicle_id):
        """更新车型"""
        vehicle, errors = VehicleModelService.update_vehicle(vehicle_id, request.data)
        if vehicle:
            serializer = VehicleModelSerializer(vehicle)
            return ApiResponse.success(data=serializer.data, message="更新成功")
        return ApiResponse.error(message=errors if isinstance(errors, str) else "更新失败", data=errors)

    @swagger_auto_schema(
        operation_summary="删除车型",
        operation_description="根据ID删除车型（软删除）",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT)}
    )
    def delete(self, request, vehicle_id):
        """删除车型"""
        success, message = VehicleModelService.delete_vehicle(vehicle_id)
        if success:
            return ApiResponse.success(message=message)
        return ApiResponse.error(message=message)