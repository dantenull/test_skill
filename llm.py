
import os
from langchain_openai import ChatOpenAI

model_name = 'qwen3-235b-a22b'
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
api_key = os.getenv('API_KEY')

llm = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    temperature=0,
)
