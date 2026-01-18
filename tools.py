import subprocess
import os
from pathlib import Path
from typing import Optional

from langchain.tools import tool


@tool
def run_python_code(
    code: Optional[str] = None, 
    script_path: Optional[str] = None, 
    script_args: Optional[list] = None
) -> str:
    """
    Run python code or script and return the output
    Args:
        code: Python code to run
        script_path: Path to python script to run
        script_args: List of arguments to pass to the script
        
    Returns:
        dict: Contains success status, stdout, stderr, and return code
    """
    timeout = 60
    try:
        if script_path:
            cmd = [
                'd:/AI/test_skill/.venv/Scripts/python.exe',
                script_path,
                *script_args
            ]
        else:
            cmd = [
                'd:/AI/test_skill/.venv/Scripts/python.exe',
                '-c',
                code
            ]
        
        # 执行并捕获输出
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        return {
            'success': process.returncode == 0,
            'stdout': process.stdout,
            'stderr': process.stderr,
            'returncode': process.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Execution timeout after {timeout} seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Error: {e}',
            'returncode': -2
        }


@tool
async def use_skill(skill_name: str, base_path: str) -> str:
    """
    Use a skill with the given name and arguments.
    
    Expected structure:
    skills/ (base_path)
    |-- skill_name/
    |   |-- SKILL.md

    Args:
        skill_name: Name of the skill to use
        base_path: Base path where all skills are stored
        
    Returns:
        str: Content of the skill file if found, otherwise an error message
    """
    base_path = Path(base_path)
    skill_path = base_path / skill_name
    # if not str(skill_path).endswith('skills') or not str(skill_path).endswith('skills/'):
    #     skill_path = skill_path / 'skills'
    skill_file = skill_path / 'SKILL.md'
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            skill_content = f.read()
    except FileNotFoundError:
        return f"Skill '{skill_name}' not found, please check the skill name and the skill path."
    return skill_content


@tool
def get_data_desc(name: str) -> str:
    """
    Get the description of a dataset(csv, json, excel) with the given name.
    
    Expected structure:
    data/ (base_path)
    |-- name.csv
    |-- name.md
    
    Args:
        name: Name of the dataset
        
    Returns:
        str: Description of the dataset
    """
    file_path = f'data/{name}.md'
    content = ''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return f"Dataset '{name}' not found, please check the dataset name and the dataset path."
    return content


@tool
def save_result(result: str, file_name: str = 'result.md') -> None:
    """
    保存一些结果到markdown文件。
    
    Args:
        result: 要保存的结果
        file_name: 要保存的文件名，注意不是路径，只是文件名
    """
    if not file_name.endswith('.md'):
        file_name += '.md'
    file_path = f'results/{file_name}'
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
    except Exception as e:
        return f'Error saving result to {file_path}: {e}'
    return f'Result saved to {file_path}'


@tool
def save_context(context: str, agent_name: str = None, context_name: str = None) -> str:
    """
    保存agent的上下文到文件。
    当已经经过了过多轮次的对话时，需要保存之前的重要的内容到文件中。以便之后取用

    Args:
        context: 上下文内容
        agent_name: 代理名称
        context_name: 上下文名称
    Returns:
        str: 保存是否成功
    """
    if not agent_name:
        agent_name = 'agent'
    if not context_name:
        context_name = 'context'
    file_path = f'contexts/{agent_name}/{context_name}.txt'
    if not os.path.exists(f'contexts/{agent_name}'):
        os.makedirs(f'contexts/{agent_name}')

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(context)
    except Exception as e:
        return f'Error saving context to {file_path}: {e}'
    return f'Context saved to {file_path}'


@tool
def get_context(agent_name: str = None, context_name: str = None) -> str:
    """
    获取agent的上下文内容。
    
    Args:
        agent_name: 代理名称
        context_name: 上下文名称
    Returns:
        str: 上下文内容
    """
    if not agent_name:
        agent_name = 'agent'
    if not context_name:
        context_name = 'context'
    file_path = f'contexts/{agent_name}/{context_name}.txt'
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            context = f.read()
    except FileNotFoundError:
        return f"Context '{context_name}' not found for agent '{agent_name}', please check the context name and the agent name."
    return context
