# -*- coding: utf-8 -*-
"""
Wilson Sonsini demo
Reads CBP Nodes and asks AI to analyze CCC improvements
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import os
from openai import OpenAI

# ===== Load environment variables =====
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

# ===== Paths =====
BASE_DIR = Path(__file__).resolve().parent
NODES_DIR = BASE_DIR / "Nodes"

PROMPT_TEMPLATE = """You are a business process improvement expert.

From the following business nodes, select those that contribute to improving the Cash Conversion Cycle (CCC),
and briefly explain why for each selected node. If applicable, relate them to DSO, DIO, or DPO.

Nodes:
{descriptions}
"""

# ===== Load nodes =====
all_nodes = {}

if not NODES_DIR.exists():
    raise FileNotFoundError(f"Nodes folder not found: {NODES_DIR}")

for i in range(1, 13):

    filename = f"e-node{i:02d}.json"
    path = NODES_DIR / filename

    if not path.exists():
        continue

    with open(path, "r", encoding="utf-8") as f:

        try:
            node = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse error in {filename}: {e}")
            continue

        node_id = node.get("node_id", f"Node{i}")

        all_nodes[node_id] = {
            "department": node.get("department", ""),
            "task_name": node.get("task_name", ""),
            "process_description": node.get("process_description", ""),
            "ccc_relation": node.get("ccc_relation", None)
        }

# ===== Build prompt =====
lines = []

for node_id, data in all_nodes.items():

    dept = data["department"]
    task = data["task_name"]
    desc = data["process_description"]
    ccc  = data["ccc_relation"]

    ccc_hint = f" [ccc_relation: {ccc}]" if ccc else ""

    lines.append(
        f"- {node_id} | {dept} | {task}{ccc_hint}\n  {desc}"
    )

descriptions = "\n".join(lines)

prompt = PROMPT_TEMPLATE.format(descriptions=descriptions)

# ===== Call AI =====
response = client.chat.completions.create(

    model="gpt-4o-mini",

    messages=[
        {"role": "system", "content": "You are a business process improvement expert."},
        {"role": "user", "content": prompt}
    ]

)

print("\n▼ ChatGPT Answer:\n")
print(response.choices[0].message.content)