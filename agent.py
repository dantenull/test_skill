import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend
from deepagents.middleware.skills import SkillsMiddleware
from langgraph.checkpoint.postgres import PostgresSaver

from tools import run_python_code, use_skill, get_data_desc, save_result, get_context, save_context

model_name = 'qwen3-235b-a22b'
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
api_key = os.getenv('API_KEY')

llm = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    temperature=0,
)


async def get_agent(
    system_prompt: str = None, 
    agent_name: str = None, 
    tools: list = None,
    checkpointer = None
) -> CompiledStateGraph:
    default_tools = [run_python_code, use_skill, get_data_desc, save_result, get_context, save_context]
    if tools is None:
        tools = default_tools
    else:
        tools.extend(default_tools)
    
    backend=FilesystemBackend(root_dir="D:/AI/test_skill/")
    skills=["D:/AI/test_skill/skills/"]
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        name=agent_name,
        checkpointer=checkpointer,
        middleware=[SkillsMiddleware(backend=backend, sources=skills)],
    )
    # agent = create_deep_agent(
    #     model=llm,
    #     tools=tools,
    #     system_prompt=system_prompt,
    #     name=agent_name,
    #     backend=FilesystemBackend(root_dir="D:/AI/test_skill/"),
    #     skills=["D:/AI/test_skill/skills/"],
    # )
    return agent
