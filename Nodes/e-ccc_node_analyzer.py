# -*- coding: utf-8 -*-
"""
Windows version for Wilson Sonsini demo
- Reads e-node01.json ... e-node12.json from a local folder
- Builds a prompt about CCC improvements
- Calls OpenAI Chat Completions
"""

import json
import os
from pathlib import Path
import openai  # pip install openai

# ====== Paths ======
BASE_DIR = Path.cwd()             # current working directory
NODES_DIR = BASE_DIR    # folder containing e-node01.json ... e-node12.json
API_KEY_FILE = BASE_DIR / "apikey.txt"

PROMPT_TEMPLATE = """You are a business process improvement expert.

From the following business nodes, select those that contribute to improving the Cash Conversion Cycle (CCC),
and briefly explain why for each selected node. If applicable, relate them to DSO, DIO, or DPO.

Nodes:
{descriptions}
"""

# ====== Load API key ======
with open(API_KEY_FILE, "r", encoding="utf-8") as f:
    api_key = f.read().strip()

openai.api_key = api_key

# ====== Load local node JSONs ======
all_nodes = {}

if not NODES_DIR.exists():
    raise FileNotFoundError(f"Nodes folder not found: {NODES_DIR}")

for i in range(1, 13):
    filename = f"e-node{i:02d}.json"   # e-node01.json ... e-node12.json
    path = NODES_DIR / filename
    if not path.exists():
        continue
    with open(path, "r", encoding="utf-8") as f:
        try:
            node = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse error in {filename}: {e}")
            continue

        node_id = node.get("node_id", f"e-node{i:02d}")
        all_nodes[node_id] = {
            "department": node.get("department", ""),
            "task_name": node.get("task_name", ""),
            "process_description": node.get("process_description", ""),
            "ccc_relation": node.get("ccc_relation", None)
        }

# ====== Build prompt ======
lines = []
for node_id, data in all_nodes.items():
    dept = data["department"]
    task = data["task_name"]
    desc = data["process_description"]
    ccc  = data["ccc_relation"]
    ccc_hint = f" [ccc_relation: {ccc}]" if ccc else ""
    lines.append(f"- {node_id} | {dept} | {task}{ccc_hint}\n  {desc}")

descriptions = "\n".join(lines)
prompt = PROMPT_TEMPLATE.format(descriptions=descriptions)

# ====== Call ChatGPT ======
client = openai.OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a business process improvement expert."},
        {"role": "user", "content": prompt}
    ]
)

print("▼ ChatGPT Answer:")
print(response.choices[0].message.content)