from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from common.responses import ApiResponse
from .services import ScriptTaskService, ScriptExecutionService
from .serializers import (
    ScriptTaskSerializer, ScriptTaskUpdateSerializer, ScriptExecutionSerializer,
    ScriptExecuteSerializer
)


class ScriptTaskView(APIView):
    """脚本任务视图"""

    @swagger_auto_schema(
        operation_summary="获取脚本任务列表",
        operation_description="获取所有脚本任务，支持按状态、类型和名称筛选",
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="状态筛选", type=openapi.TYPE_STRING),
            openapi.Parameter('script_type', openapi.IN_QUERY, description="脚本类型", type=openapi.TYPE_STRING),
            openapi.Parameter('name', openapi.IN_QUERY, description="脚本名称模糊搜索", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ScriptTaskSerializer(many=True)}
    )
    def get(self, request):
        """获取脚本任务列表"""
        status = request.query_params.get('status')
        script_type = request.query_params.get('script_type')
        name = request.query_params.get('name')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        queryset = ScriptTaskService.get_all_scripts(status=status, script_type=script_type, name=name)

        return ApiResponse.paginated_response(
            queryset=queryset,
            page=page,
            page_size=page_size,
            serializer_class=ScriptTaskSerializer,
            request=request
        )

    @swagger_auto_schema(
        operation_summary="创建脚本任务",
        operation_description="创建新的脚本任务",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='脚本名称'),
                'script_type': openapi.Schema(type=openapi.TYPE_STRING, description='脚本类型',
                                              enum=['bash', 'python']),
                'return_type': openapi.Schema(type=openapi.TYPE_STRING, description='返回类型',
                                              enum=['text', 'json', 'html', 'xml']),
                'parameters': openapi.Schema(type=openapi.TYPE_OBJECT, description='脚本参数'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='脚本内容'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='备注说明'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='状态',
                                         enum=['active', 'inactive', 'draft']),
                'timeout': openapi.Schema(type=openapi.TYPE_INTEGER, description='超时时间(秒)'),
            },
            required=['name', 'script_type', 'content']
        ),
        responses={200: ScriptTaskSerializer()}
    )
    def post(self, request):
        """创建脚本任务"""
        script, errors = ScriptTaskService.create_script(request.data)
        if script:
            serializer = ScriptTaskSerializer(script)
            return ApiResponse.success(data=serializer.data, message="脚本创建成功")
        return ApiResponse.error(message="创建失败", data=errors)


class ScriptTaskDetailView(APIView):
    """脚本任务详情视图"""

    @swagger_auto_schema(
        operation_summary="获取脚本任务详情",
        operation_description="根据ID获取脚本任务详情",
        responses={200: ScriptTaskSerializer()}
    )
    def get(self, request, script_id):
        """获取脚本任务详情"""
        script = ScriptTaskService.get_script_by_id(script_id)
        if not script:
            return ApiResponse.error(message="脚本不存在", code=404)

        serializer = ScriptTaskSerializer(script)
        return ApiResponse.success(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="更新脚本任务",
        operation_description="根据ID更新脚本任务信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='脚本名称'),
                'script_type': openapi.Schema(type=openapi.TYPE_STRING, description='脚本类型'),
                'return_type': openapi.Schema(type=openapi.TYPE_STRING, description='返回类型'),
                'parameters': openapi.Schema(type=openapi.TYPE_OBJECT, description='脚本参数'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='脚本内容'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='备注说明'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='状态'),
                'timeout': openapi.Schema(type=openapi.TYPE_INTEGER, description='超时时间(秒)'),
            }
        ),
        responses={200: ScriptTaskSerializer()}
    )
    def put(self, request, script_id):
        """更新脚本任务"""
        script, errors = ScriptTaskService.update_script(script_id, request.data)
        if script:
            serializer = ScriptTaskSerializer(script)
            return ApiResponse.success(data=serializer.data, message="更新成功")
        return ApiResponse.error(message=errors if isinstance(errors, str) else "更新失败", data=errors)

    @swagger_auto_schema(
        operation_summary="删除脚本任务",
        operation_description="根据ID删除脚本任务（软删除）",
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT)}
    )
    def delete(self, request, script_id):
        """删除脚本任务"""
        success, message = ScriptTaskService.delete_script(script_id)
        if success:
            return ApiResponse.success(message=message)
        return ApiResponse.error(message=message)


class ScriptExecuteView(APIView):
    """脚本执行视图"""

    @swagger_auto_schema(
        operation_summary="执行脚本任务",
        operation_description="执行指定的脚本任务",
        request_body=ScriptExecuteSerializer,
        responses={200: ScriptExecutionSerializer()}
    )
    def post(self, request, script_id):
        """执行脚本任务"""
        execution, errors = ScriptTaskService.execute_script(
            script_id,
            request.data.get('parameters', {})
        )
        if execution:
            serializer = ScriptExecutionSerializer(execution)
            return ApiResponse.success(data=serializer.data, message="脚本开始执行")
        return ApiResponse.error(message=errors if isinstance(errors, str) else "执行失败", data=errors)


class ScriptExecutionView(APIView):
    """脚本执行记录视图"""

    @swagger_auto_schema(
        operation_summary="获取执行记录列表",
        operation_description="获取脚本执行记录，可按脚本和状态筛选",
        manual_parameters=[
            openapi.Parameter('script_id', openapi.IN_QUERY, description="脚本ID", type=openapi.TYPE_STRING),
            openapi.Parameter('status', openapi.IN_QUERY, description="执行状态", type=openapi.TYPE_STRING,
                            enum=['running', 'success', 'failed', 'timeout', 'cancelled']),
            openapi.Parameter('page', openapi.IN_QUERY, description="页码", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="每页数量", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ScriptExecutionSerializer(many=True)}
    )
    def get(self, request):
        """获取执行记录列表"""
        script_id = request.query_params.get('script_id')
        status = request.query_params.get('status')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        if script_id:
            queryset = ScriptExecutionService.get_executions_by_script(script_id, status=status)
        else:
            queryset = ScriptExecutionService.get_all_executions(status=status)

        return ApiResponse.paginated_response(
            queryset=queryset,
            page=page,
            page_size=page_size,
            serializer_class=ScriptExecutionSerializer,
            request=request
        )


class ScriptExecutionDetailView(APIView):
    """脚本执行记录详情视图"""

    @swagger_auto_schema(
        operation_summary="获取执行记录详情",
        operation_description="根据ID获取执行记录详情",
        responses={200: ScriptExecutionSerializer()}
    )
    def get(self, request, execution_id):
        """获取执行记录详情"""
        execution = ScriptExecutionService.get_execution_by_id(execution_id)
        if not execution:
            return ApiResponse.error(message="执行记录不存在", code=404)

        serializer = ScriptExecutionSerializer(execution)
        return ApiResponse.success(data=serializer.data)