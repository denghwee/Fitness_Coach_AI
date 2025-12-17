from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

res = client.responses.create(
    model="gpt-4o-mini",
    input="Tạo meal plan cho tôi"
)

print(res.output_text)
