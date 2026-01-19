import asyncio
import os
from uuid import uuid4
from textwrap import dedent

from colorama import Fore, Back, Style
from jinja2 import Template

from agent import get_agent
from read_dotenv import read_dotenv

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

read_dotenv('.')


async def run_agent(query: str, system_prompt: str = None, agent_name: str = 'agent', thread_id: str = "1"):
    agent = await get_agent(system_prompt=system_prompt, agent_name=agent_name)
    messages = {"role": "user", "content": query}
    async for mode, info in agent.astream(
        {"messages": [messages]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode=['messages', 'updates'],
    ):
        if mode == 'messages':
            chunk, step = info
            if chunk.content and step['langgraph_node'] == 'model':
                print(Fore.GREEN + chunk.content + Style.RESET_ALL, end='')
        elif mode == 'updates':
            print('\n')
            content = ''
            if 'model' in info:
                message = info['model']['messages'][-1]
                if message.tool_calls:
                    content = f'ToolCalls:\n\n'
                    for tool_call in message.tool_calls:
                        content += f'ToolName: {tool_call["name"]}\nArgs:\n{tool_call["args"]}\n'
            elif 'tools' in info:
                message = info['tools']['messages'][-1]
                content = f'ToolName: {message.name}\n'
                if message.name != 'use_skill':
                    content += f'Content:\n{message.content}'
            else:
                for k in info:
                    if k.startswith('add_important_context'):
                        continue
                    content = str(info)
                    break
            if content:
                print(Fore.BLUE + content + Style.RESET_ALL)


def get_system_prompt():
    with open('system_prompt.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()
    return system_prompt


async def main():
    system_prompt = get_system_prompt()
    query = dedent("""
    分析这个目录下的csv文件: D:/AI/test_skill/data/instagram_usage_lifestyle.csv
    """)
    thread_id = str(uuid4())
    print(f"thread_id: {thread_id}")
    agent_name = 'data_analysis'
    await run_agent(query, system_prompt=system_prompt, thread_id=thread_id, agent_name=agent_name)


if __name__ == "__main__":
    asyncio.run(main())
