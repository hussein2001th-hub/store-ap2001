import os, re

path = r'c:\Users\حسين\Desktop\app\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add cache busters
html = re.sub(r'(\.css|\.js)"', r'\1?v=4.0"', html)

# Let's also check layout.css for any explicit black colors and change them to light blue.
# And maybe change the balance-card to a light blue gradient instead of white?
# User said "change every black color to light blue".
# I'll update variables.css to make the text or backgrounds light blue? No, text must be dark to be readable.
# The user's screenshot had a BLACK balance-card. That means the user was seeing a black balance card.
# How is the balance-card styled? It is:
# background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);
# If it showed as black, it was definitely an old cache.
# But wait! If the user *wants* the balance card to be light blue instead of black (they thought the black was intended), let's change it to light blue!

css_path = r'c:\Users\حسين\Desktop\app\assets\css\layout.css'
with open(css_path, 'r', encoding='utf-8') as f:
    layout_css = f.read()

# Make balance card light blue
layout_css = layout_css.replace('background: linear-gradient(135deg, #ffffff 0%, #f1f3f5 100%);', 
                                'background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);')

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(layout_css)


with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Cache busters added and balance card made light blue!')
