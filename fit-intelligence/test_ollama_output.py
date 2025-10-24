#!/usr/bin/env python3
"""Test Ollama output to debug parsing"""

import subprocess
import re
import json

query = "wind sites over 100kw in berkshire"
print(f"Testing query: {query}")

# Call Ollama
result = subprocess.run(
    ["ollama", "run", "gpt-oss-fit-enhanced", query],
    capture_output=True,
    text=True,
    timeout=30
)

print("\n=== Raw Output ===")
print(repr(result.stdout[:500]))

# Clean up
response = result.stdout.strip()

# Remove ANSI codes
response = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', response)
response = re.sub(r'\[\?[0-9]+[hl]', '', response)
response = re.sub(r'\[[0-9]+[GK]', '', response)

print("\n=== After ANSI cleanup ===")
print(repr(response[:500]))

# Extract after thinking
if "done thinking" in response:
    response = response.split("done thinking.")[-1].strip()
    print("\n=== After extracting post-thinking ===")
    print(repr(response))

# Try to find JSON
json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
if json_match:
    json_str = json_match.group()
    print("\n=== Found JSON string ===")
    print(json_str)
    
    try:
        parsed = json.loads(json_str)
        print("\n=== Parsed JSON ===")
        print(json.dumps(parsed, indent=2))
    except Exception as e:
        print(f"\nError parsing: {e}")
else:
    print("\n=== No JSON found ===")
    # Try line by line
    lines = response.split('\n')
    for i, line in enumerate(lines):
        if '{' in line:
            print(f"Line {i}: {repr(line[:100])}")