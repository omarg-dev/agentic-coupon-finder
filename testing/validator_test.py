import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.validator.agent import run_validator

if "GEMINI_API_KEY" not in os.environ:
    print("❌ Error: GEMINI_API_KEY is missing.")
    exit(1)

print("------------------------------------------------")
print("🧪 TESTING MODULE 3: THE VALIDATOR (AGENT)")
print("------------------------------------------------")

target = input("Enter a domain to validate (must have coupons in DB): ").strip()

# Warning for the user
print("\n⚠️  HEADS UP: This will open a Chromium browser.")
print("⚠️  Do not interfere with the window while the AI is working.")
print("------------------------------------------------")

run_validator(target)