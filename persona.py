from pathlib import Path

BASE_DIR = Path(**file**).parent

CONSTITUTION_FILE = BASE_DIR / "AI_ANCHOR_CONSTITUTION.md"
LORE_FILE = BASE_DIR / "AI_ANCHOR_LORE.md"

def load_persona():
constitution = ""
lore = ""

```
if CONSTITUTION_FILE.exists():
    constitution = CONSTITUTION_FILE.read_text(
        encoding="utf-8"
    )

if LORE_FILE.exists():
    lore = LORE_FILE.read_text(
        encoding="utf-8"
    )

return f"""
```

{constitution}

{lore}
"""
