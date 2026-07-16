import os
import glob

frontend_dir = r"d:\college\SystemSeige\frontend\app"
tsx_files = glob.glob(os.path.join(frontend_dir, "**", "*.tsx"), recursive=True)

for file in tsx_files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple replacement of $ with ₹ in the UI text, excluding strings where $ is used for template literals
    # We only want to replace $ if it's used for currency representation. 
    # Let's replace '($)' with '(₹)'
    content = content.replace("($)", "(₹)")
    # Replace '$' before variables like `${` but wait, string interpolation is `${var}`.
    # To replace literal dollar signs, we look for $ followed by { (template literal) and skip it.
    # We can replace '$' followed by '{' with a placeholder, then replace all '$' with '₹', then put '${' back.
    
    content = content.replace("${", "PLACEHOLDER_TEMP_VAR")
    content = content.replace("$", "₹")
    content = content.replace("PLACEHOLDER_TEMP_VAR", "${")
    
    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Replaced $ with ₹ in {len(tsx_files)} files.")
