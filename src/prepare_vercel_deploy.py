import shutil
import os

# 1. Copy outputs/dashboard.html to root index.html so Vercel serves it automatically
shutil.copyfile('outputs/dashboard.html', 'index.html')
print(f"index.html successfully created at root ({os.path.getsize('index.html')} bytes).")

# 2. Create vercel.json
vercel_config = """{
  "version": 2,
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}"""

with open('vercel.json', 'w', encoding='utf-8') as f:
    f.write(vercel_config)
print("vercel.json created.")

# 3. Create .gitignore to keep repo clean and light for GitHub/Vercel
gitignore_content = """# Data files
data/Data Pack/
data/__MACOSX/
*.parquet
*.csv.gz

# Python cache
__pycache__/
*.pyc

# Local environments
.venv/
env/
"""

with open('.gitignore', 'w', encoding='utf-8') as f:
    f.write(gitignore_content)
print(".gitignore created.")
