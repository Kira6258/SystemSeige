import sys
log_file = r"C:\Users\Kira\.gemini\antigravity-ide\brain\1014e164-79ad-431c-b2aa-a244dbcedfb5\.system_generated\tasks\task-779.log"
with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "ERROR" in line or "Exception" in line or "Traceback" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 40)
        print("".join(lines[start:end]))
        break
