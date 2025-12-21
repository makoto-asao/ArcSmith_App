import re

filepath = r'c:\Users\Makochi\OneDrive\Git\ArcSmith_App\app.py'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Remove lines containing the ineffective wrappers
    if 'st.markdown(\'<div class="stCard">\'' in line:
        continue
    if 'st.markdown(\'</div>\'' in line:
        continue
    if 'st.markdown(f\'<div class="{anim_class}">\'' in line:
        continue
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8', newline='') as f:
    f.writelines(new_lines)

print("Removed all ineffective wrappers from app.py.")
