#!/usr/bin/env python
"""
Test to verify the Add User button detection issue
"""

content = """<a href="/staff/users/add/" class="btn-admin btn-admin-primary">
    <i class="fas fa-plus"></i>
    Add User
</a>"""

search_text = "Add User"
found_wrong = search_text in content.lower()  # What the test is doing
found_correct = search_text.lower() in content.lower()  # What it should do

print(f"Content: {content}")
print(f"Searching for: '{search_text}'")
print(f"In lowercase content: '{content.lower()}'")
print(f"Test's method (wrong): {found_wrong}")
print(f"Correct method: {found_correct}")
