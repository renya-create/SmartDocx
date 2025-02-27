import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# print(os.getenv("API_KEY"))
# print(os.getenv("API_VERSION"))
# print(os.getenv("AZURE_OPENAI_ENDPOINT"))
# print(os.getenv("MODEL_NAME"))  

# AzureOpenAI クライアントを初期化
client = AzureOpenAI(
    api_key=os.getenv("API_KEY"),  
    api_version=os.getenv("API_VERSION", "2024-08-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_text(input_text, instruction):

    prompt = f"<input>{input_text}</input><instruction>{instruction}</instruction>"
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4o"),
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            {"role": "user", "content": prompt},
        ]
    )
    
    return response.choices[0].message.content