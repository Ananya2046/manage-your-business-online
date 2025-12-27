import google.generativeai as genai
import os

# Configure with your API key
api_key = os.getenv("AIzaSyB34TUpMM4lfOcNhTPakYF90vzGtV8NWcw")
genai.configure(api_key=api_key)

print("🔍 Checking available Gemini models...")
print("="*50)

# List all models
models = genai.list_models()

# Filter for content generation models
generation_models = []
for model in models:
    if 'generateContent' in model.supported_generation_methods:
        generation_models.append(model.name)

print(f"✅ Found {len(generation_models)} models that support generateContent:\n")

# Show available models
for i, model_name in enumerate(generation_models, 1):
    print(f"{i}. {model_name}")

# Test specific models
test_models = [
    'gemini-2.5-flash-lite',      # 2.5 Flash-Lite
    'gemini-3.0-flash-exp',      # Gemini 3 Flash
    'gemini-1.5-flash-latest',   # Stable
    'gemini-1.5-pro-latest',     # Pro
]

print("\n🧪 Testing specific models...")
print("="*50)

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✅ {model_name}: WORKS")
    except Exception as e:
        print(f"❌ {model_name}: {str(e)[:100]}...")
