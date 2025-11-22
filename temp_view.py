from pathlib import Path
lines=Path("frontend/src/App.vue").read_text("utf-8").splitlines()
start = 0
for idx,line in enumerate(lines,1):
    if '<div class="sidebar-bottom"' in line:
        start = idx-1
        break
for i in range(start, start+40):
    print(f"{i+1}: {lines[i]}")
