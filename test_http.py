from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

print("SUPABASE_URL:", os.environ.get("SUPABASE_URL"))
print("OPENROUTER_API_KEY set:", bool(os.environ.get("OPENROUTER_API_KEY")))

# Test Supabase
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)
print("Testing Supabase...")
try:
    resp = supabase.table("participants").select("*").limit(1).execute()
    print("Supabase OK. Got:", resp.data)
except Exception as e:
    print("Supabase error:", e)

# Test OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

print("Testing OpenRouter...")
try:
    r = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet"),
        messages=[{"role": "user", "content": "Say hi in one sentence."}],
    )
    print("OpenRouter OK. Response:", r.choices[0].message.content)
except Exception as e:
    print("OpenRouter error:", e)
