"""
Phase 1 verification script — run from the project root:
    python test/verify_phase1.py
"""
import sys
import os
import json

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline.pipeline import ProcessingPipeline
from app.utils.validator import is_supported_file

# ── Setup ──────────────────────────────────────────────────────────────────────
os.makedirs("data/input", exist_ok=True)
os.makedirs("data/output", exist_ok=True)

with open("data/input/test_users.csv", "w", encoding="utf-8") as f:
    f.write("id,name,role\n1,Alice,Admin\n2,Bob,User\n2,Bob,User\n")

with open("data/input/test_config.json", "w", encoding="utf-8") as f:
    json.dump({"status": "active", "version": 1.0}, f)

with open("data/input/sample_array.json", "w", encoding="utf-8") as f:
    json.dump([{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], f)

with open("data/input/test_sample.txt", "w", encoding="utf-8") as f:
    f.write("hello world\n\n  blank above\nend\n")

# ── Tests ──────────────────────────────────────────────────────────────────────
pipeline = ProcessingPipeline()
print("=== PHASE 1 VERIFICATION ===")

print("\n--- Test 1: CSV ---")
r = pipeline.run("data/input/test_users.csv")
print(f"Result: {r}  (expected: True)")

print("\n--- Test 2: Flat JSON ---")
r = pipeline.run("data/input/test_config.json")
print(f"Result: {r}  (expected: True)")

print("\n--- Test 3: Array JSON ---")
r = pipeline.run("data/input/sample_array.json")
print(f"Result: {r}  (expected: True)")

print("\n--- Test 4: TXT ---")
r = pipeline.run("data/input/test_sample.txt")
print(f"Result: {r}  (expected: True)")

print("\n--- Test 5: Unsupported (.png) ---")
r = pipeline.run("data/input/test_image.png")
print(f"Result: {r}  (expected: False)")

print("\n--- Test 6: Case-insensitive extension check ---")
checks = [
    ("file.CSV",  True),
    ("file.JSON", True),
    ("file.TXT",  True),
    ("file.png",  False),
    ("file.pdf",  False),
]
for name, expected in checks:
    result = is_supported_file(name)
    status = "OK" if result == expected else "FAIL"
    print(f"  [{status}] {name}: {result}  (expected: {expected})")

print("\n=== Output files ===")
for fname in sorted(os.listdir("data/output")):
    print(f"  {fname}")
