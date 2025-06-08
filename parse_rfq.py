import os
import json
import re
from typing import List


FIELDS = [
    "title",
    "solicitation number",
    "agency",
    "submission deadline",
    "scope of work",
    "evaluation criteria",
    "required qualifications",
    "submission instructions",
    "contact information",
]


def extract_section(lines: List[str], start_keywords: List[str], end_keywords: List[str]) -> str:
    start_idx = None
    for i, line in enumerate(lines):
        l = line.lower()
        if any(k in l for k in start_keywords):
            start_idx = i + 1
            break
    if start_idx is None:
        return ""
    collected = []
    for j in range(start_idx, len(lines)):
        l = lines[j].strip()
        if not l:
            # stop at blank line
            if collected:
                break
            else:
                continue
        if any(k in l.lower() for k in end_keywords):
            break
        collected.append(l.lstrip('- ').lstrip('•').strip())
    return " ".join(collected).strip()


def parse_rfq(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines()]
    data = {field: "" for field in FIELDS}

    # agency: first non-empty line
    for line in lines:
        if line:
            data["agency"] = line
            break

    # solicitation number
    for line in lines:
        if "rfp #" in line.lower():
            data["solicitation number"] = line.split("#", 1)[1].strip().lstrip(":").strip()
            break

    # title
    title_idx = None
    for i, line in enumerate(lines):
        if "rfp title" in line.lower():
            title_text = line.split(":", 1)[1].strip()
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                lower = next_line.lower()
                if not next_line or "due date" in lower or "rfp due" in lower:
                    break
                if next_line.endswith(":"):
                    break
                title_text += " " + next_line
                j += 1
            data["title"] = title_text
            title_idx = i
            break

    # submission deadline
    for line in lines:
        if "due date" in line.lower():
            data["submission deadline"] = line.split(":",1)[1].strip()
            break

    # scope of work (brief scope + deliverables + background)
    scope = extract_section(
        lines,
        ["brief scope of services"],
        ["evaluation criteria", "proposal requirements"]
    )
    if scope:
        data["scope of work"] = scope

    # evaluation criteria
    eval_criteria = extract_section(
        lines,
        ["evaluation criteria"],
        ["proposal requirements", "contract duration"]
    )
    if eval_criteria:
        data["evaluation criteria"] = eval_criteria

    # required qualifications - not explicitly present; use proposal requirements if available
    qualifications = extract_section(
        lines,
        ["required qualifications"],
        ["submission format", "proposal requirements"]
    )
    if not qualifications:
        qualifications = extract_section(
            lines,
            ["proposal requirements"],
            ["contract duration", "submission format"]
        )
    if qualifications:
        data["required qualifications"] = qualifications

    # submission instructions
    instructions_parts = []
    for line in lines:
        if line.lower().startswith("submit to"):
            instructions_parts.append(line)
    instr_section = extract_section(
        lines,
        ["submission format"],
        ["compliance"]
    )
    if instr_section:
        instructions_parts.append(instr_section)
    if instructions_parts:
        data["submission instructions"] = " ".join(instructions_parts)

    # contact information
    contacts = []
    for line in lines:
        if line.lower().startswith("contact:") or line.lower().startswith("backup contact"):
            contacts.append(line)
    if contacts:
        data["contact information"] = " ".join(contacts)

    return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse RFQ text into structured data")
    parser.add_argument("input", help="Path to cleaned txt file")
    parser.add_argument("output", help="Path to output JSON file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()
    data = parse_rfq(text)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
