import os
from pathlib import Path

from jinja2 import Template
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend
from deepagents.middleware.skills import SkillsMiddleware
from langchain.agents import AgentState
from langchain.agents.middleware import before_model, TodoListMiddleware
from langchain.messages import HumanMessage, RemoveMessage
from langgraph.runtime import Runtime
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from tools import (
    run_python_code, 
    use_skill, 
    get_data_desc, 
    read_file,
    write_file,
    ls,
    task_done
)
from llm import llm
from constants import BASE_PATH


async def get_agent(
    system_prompt: str = None, 
    agent_name: str = None, 
    tools: list = None,
    checkpointer = None
) -> CompiledStateGraph:
    with open('./important_context.md', 'r', encoding='utf-8') as f:
        important_context = f.read()
        important_context = Template(important_context).render(
            base_path=BASE_PATH,
            agent_name=agent_name,
        )
    system_prompt += f'\n{important_context}'

    context_path = Path(f'./context/{agent_name}.md')
    if not os.path.exists(context_path):
        os.makedirs(context_path)
    clear_messages_file = context_path / 'clear_messages.txt'
    with open(clear_messages_file, 'w', encoding='utf-8') as f:
        f.write('false')

    @before_model
    def add_important_context(state: AgentState, runtime: Runtime):
        messages = state['messages']
        print(f'---------------message长度 {len(messages)}-----------------')
        is_clear = 'false'
        with open(clear_messages_file, 'r', encoding='utf-8') as f:
            is_clear = f.read()
        if is_clear == 'true':
            with open(clear_messages_file, 'w', encoding='utf-8') as f:
                f.write('false')
            if len(messages) < 5:
                return
            first_msg = messages[0]
            recent_messages = messages[-3:]
            new_messages = [first_msg] + recent_messages
            new_messages.append(HumanMessage(content=important_context))
            print(f'clear messages {len(new_messages)}')
            return {
                'messages': [
                    RemoveMessage(id=REMOVE_ALL_MESSAGES),
                    *new_messages
                ]
            }
        # last_message = messages[-1]
        # if last_message.type == 'human':
        #     messages[-1].content += f'\n{important_context}'
        # else:
        #     messages.append(HumanMessage(content=important_context))
        # return {'messages': messages}


    default_tools = [
        run_python_code, use_skill, get_data_desc, 
        read_file, write_file, ls, task_done, 
    ]
    if tools is None:
        tools = default_tools
    else:
        tools.extend(default_tools)
    
    backend=FilesystemBackend(root_dir="D:/AI/test_skill/")
    skills=["D:/AI/test_skill/skills/"]
    middlewares = [
        SkillsMiddleware(backend=backend, sources=skills),
        PatchToolCallsMiddleware(),
        TodoListMiddleware(),
        add_important_context,
    ]
    
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        name=agent_name,
        checkpointer=checkpointer,
        middleware=middlewares,
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
