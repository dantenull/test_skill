import asyncio
import os
from uuid import uuid4
from textwrap import dedent

from colorama import Fore, Back, Style
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agent import get_agent
from read_dotenv import read_dotenv

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

read_dotenv('.')


async def run_agent(query: str, system_prompt: str = None, thread_id: str = "1"):
    pg_user = os.getenv('PGUSER')
    pg_db = os.getenv('PGDB')
    pg_pwd = os.getenv('PGPASSWORD')
    pg_port = os.getenv('PGPORT')
    DB_URI = f'postgresql://{pg_user}:{pg_pwd}@localhost:{pg_port}/{pg_db}?sslmode=disable'
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()
        agent = await get_agent(system_prompt=system_prompt, checkpointer=checkpointer)
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
                        content = f'ToolCalls:\n{message.tool_calls}'
                elif 'tools' in info:
                    message = info['tools']['messages'][-1]
                    content = f'ToolName: {message.name}\nContent:\n{message.content}'
                else:
                    content = str(info)
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
    # 196ad670-bd17-433f-ad61-5dba70987fc0
    thread_id = str(uuid4())
    print(f"thread_id: {thread_id}")
    await run_agent(query, system_prompt=system_prompt, thread_id=thread_id)


if __name__ == "__main__":
    asyncio.run(main())
