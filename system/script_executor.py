import subprocess
import tempfile
import os
import json
import time
from datetime import datetime
from django.conf import settings
from typing import Tuple, Dict, Any


class ScriptExecutor:
    """脚本执行器"""

    def __init__(self, script_task):
        self.script_task = script_task
        self.temp_dir = tempfile.mkdtemp()

    def execute(self, parameters: Dict[str, Any] = None) -> Tuple[bool, str, str, float]:
        """
        执行脚本
        返回: (是否成功, 输出内容, 错误信息, 执行时间)
        """
        parameters = parameters or {}
        start_time = time.time()

        try:
            if self.script_task.script_type == 'bash':
                return self._execute_bash(parameters, start_time)
            elif self.script_task.script_type == 'python':
                return self._execute_python(parameters, start_time)
            else:
                return False, "", "不支持的脚本类型", time.time() - start_time
        except Exception as e:
            return False, "", str(e), time.time() - start_time
        finally:
            self._cleanup()

    def _execute_bash(self, parameters: Dict[str, Any], start_time: float) -> Tuple[bool, str, str, float]:
        """执行Bash脚本"""
        # 创建临时脚本文件
        script_file = os.path.join(self.temp_dir, 'script.sh')

        # 准备脚本内容，添加参数处理
        script_content = self._prepare_bash_script(parameters)

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 设置执行权限
        os.chmod(script_file, 0o755)

        # 执行脚本
        try:
            result = subprocess.run(
                ['bash', script_file],
                capture_output=True,
                text=True,
                timeout=self.script_task.timeout,
                cwd=self.temp_dir
            )

            execution_time = time.time() - start_time

            # 合并标准输出和标准错误输出，提供完整的脚本执行信息
            combined_output = ""
            if result.stdout:
                combined_output += f"=== 标准输出 ===\n{result.stdout}\n"
            if result.stderr:
                combined_output += f"=== 错误输出 ===\n{result.stderr}\n"
            
            if result.returncode == 0:
                return True, combined_output.strip(), result.stderr, execution_time
            else:
                return False, combined_output.strip(), result.stderr, execution_time

        except subprocess.TimeoutExpired:
            return False, "", "脚本执行超时", time.time() - start_time

    def _execute_python(self, parameters: Dict[str, Any], start_time: float) -> Tuple[bool, str, str, float]:
        """执行Python脚本"""
        # 创建临时脚本文件
        script_file = os.path.join(self.temp_dir, 'script.py')

        # 准备脚本内容，添加参数处理
        script_content = self._prepare_python_script(parameters)

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        # 执行脚本
        try:
            result = subprocess.run(
                ['python3', script_file],
                capture_output=True,
                text=True,
                timeout=self.script_task.timeout,
                cwd=self.temp_dir
            )

            execution_time = time.time() - start_time

            # 合并标准输出和标准错误输出，提供完整的脚本执行信息
            combined_output = ""
            if result.stdout:
                combined_output += f"=== 标准输出 ===\n{result.stdout}\n"
            if result.stderr:
                combined_output += f"=== 错误输出 ===\n{result.stderr}\n"
            
            if result.returncode == 0:
                return True, combined_output.strip(), result.stderr, execution_time
            else:
                return False, combined_output.strip(), result.stderr, execution_time

        except subprocess.TimeoutExpired:
            return False, "", "脚本执行超时", time.time() - start_time

    def _prepare_bash_script(self, parameters: Dict[str, Any]) -> str:
        """准备Bash脚本内容"""
        param_exports = []
        for key, value in parameters.items():
            # 安全处理参数值
            safe_value = str(value).replace('"', '\\"')
            param_exports.append(f'export {key}="{safe_value}"')

        param_section = '\n'.join(param_exports) if param_exports else ''

        return f"""#!/bin/bash
# 自动生成的参数导出
{param_section}

# 用户脚本内容
{self.script_task.content}
"""

    def _prepare_python_script(self, parameters: Dict[str, Any]) -> str:
        """准备Python脚本内容"""
        param_dict = json.dumps(parameters, ensure_ascii=False, indent=2)

        return f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
import os

# 自动生成的参数字典
PARAMS = {param_dict}

# 用户脚本内容
{self.script_task.content}
"""

    def _cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass
