import os
import glob

frontend_dir = r"d:\college\SystemSeige\frontend\app"
tsx_files = glob.glob(os.path.join(frontend_dir, "**", "*.tsx"), recursive=True)

for file in tsx_files:
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        # Do not touch API paths or router paths
        if "api." in line or "router.push" in line or "Link href=" in line or "strokeDash" in line:
            new_lines.append(line)
            continue
            
        # Replace $ with ₹
        # In JSX, <td>${var}</td> renders as $val. We want <td>₹{var}</td>
        # For template literals like `${analysis.computation.stated_emi.toFixed(2)}`, if it's meant to render a dollar sign, it's usually written as `$${` or just `${` inside JSX.
        # Let's replace `$${` with `₹${`
        new_line = line.replace("$$", "₹$")
        
        # Replace <td>${...}</td> with <td>₹{...}</td> by just replacing `${` with `₹{` ONLY if it's inside HTML-like text
        new_line = new_line.replace(">${", ">₹{")
        
        # Also replace standalone $
        if "of $" in new_line:
            new_line = new_line.replace("of $", "of ₹")
            
        if "<strong>$" in new_line:
            new_line = new_line.replace("<strong>$", "<strong>₹")
            
        if "<td>$" in new_line:
            new_line = new_line.replace("<td>$", "<td>₹")
            
        if ">$" in new_line:
            new_line = new_line.replace(">$", ">₹")
            
        if "text-success\">$" in new_line:
            new_line = new_line.replace("\">$", "\">₹")

        if "text-warning\">$" in new_line:
            new_line = new_line.replace("\">$", "\">₹")
            
        if "muted\">$" in new_line:
            new_line = new_line.replace("\">$", "\">₹")
            
        new_lines.append(new_line)
        
    with open(file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

print("Currency replaced safely.")
