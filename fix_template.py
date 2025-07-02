#!/usr/bin/env python
"""Fix the user_edit.html template by removing extra content"""

file_path = 'templates/staff/users/user_edit.html'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep only lines up to the end of the template (line 844)
fixed_lines = lines[:844]

# Write back the fixed content
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"Fixed {file_path} - removed extra content after line 844")
print(f"Total lines: {len(lines)} -> {len(fixed_lines)}")
