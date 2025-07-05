import os
import argparse
from pathlib import Path

def create_single_script(name):
    folder = Path(name)
    folder.mkdir(exist_ok=True)
    (folder / "main.py").write_text("""# Main Script\ndef main():\n\tprint(\"Main Script Running\")\n\nif __name__ == \"__main__\":\n\tmain()""")
    (folder / "README.md").write_text(f"# {name}\n\nSingle Script Project.")
    (folder / "requirements.txt").write_text("")
    (folder / "todo.md").write_text("ToDo List: \n- [ ]")
    print(f"✅ Created single-script project: {folder}")

def create_multi_script(name):
    base = Path(name)
    src = base / "scripts"
    tests = base / "tests"
    
    # Create folders
    src.mkdir(parents=True, exist_ok=True)
    tests.mkdir(exist_ok=True)
    
    # Add files
    (src / "__init__.py").touch() 
    (src / f"{name}.py").write_text(f"# Script {name}\n")
    (tests / "__init__.py").touch()
    (tests / f"test_{name}.py").write_text(f"# Tests for {name}\n")
    (base / "main.py").write_text("""# Main Script\ndef main():\n\tprint(\"Main Script Running\")\n\nif __name__ == \"__main__\":\n\tmain()""")
    (base / "README.md").write_text(f"# {name}\n\nMulti-module project.")
    (base / "requirements.txt").touch()
    (base / "todo.md").write_text("ToDo List: \n- [ ]")

    print(f"✅ Created multi-script project: {base}")

def main():
    print("📦 Python Project Template Generator")
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', choices=['single','multi'], required=True)
    parser.add_argument('-n', '--name', required=True)
    args = parser.parse_args()

    if args.type == 'single':
        create_single_script(args.name)
    else:
        create_multi_script(args.name)

if __name__ == "__main__":
    main()