"""
Verify that the agent modules are properly structured without running them.
"""

import ast
import sys
from pathlib import Path


def verify_python_file(file_path: Path) -> dict:
    """Verify a Python file's structure."""
    with open(file_path) as f:
        code = f.read()

    try:
        tree = ast.parse(code)

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module} import {', '.join([a.name for a in node.names])}")
            elif isinstance(node, ast.Import):
                imports.append(f"import {', '.join([a.name for a in node.names])}")

        return {
            "valid": True,
            "classes": classes,
            "functions": functions,
            "imports": imports[:10],  # First 10 imports
            "error": None
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": str(e)
        }


def main():
    print("=" * 70)
    print("Verifying Iterator and Publisher Agents")
    print("=" * 70 + "\n")

    backend_path = Path(__file__).parent
    agents_path = backend_path / "app" / "agents"

    # Files to verify
    files = {
        "Iterator Agent": agents_path / "iterator.py",
        "Publisher Agent": agents_path / "publisher.py",
        "__init__.py": agents_path / "__init__.py"
    }

    all_valid = True

    for name, file_path in files.items():
        print(f"Checking {name}...")
        print(f"  Path: {file_path}")

        if not file_path.exists():
            print(f"  ERROR: File does not exist!\n")
            all_valid = False
            continue

        result = verify_python_file(file_path)

        if result["valid"]:
            print(f"  Syntax: Valid")
            if result["classes"]:
                print(f"  Classes: {', '.join(result['classes'])}")
            if result["functions"]:
                print(f"  Methods/Functions: {len(result['functions'])} defined")
            print()
        else:
            print(f"  Syntax: INVALID")
            print(f"  Error: {result['error']}\n")
            all_valid = False

    print("=" * 70)

    # Verify expected structure
    print("\nStructure Verification:")
    print("-" * 70)

    # Check Iterator Agent
    iterator_result = verify_python_file(files["Iterator Agent"])
    if "IteratorAgent" in iterator_result.get("classes", []):
        print("✓ IteratorAgent class found")
    else:
        print("✗ IteratorAgent class NOT found")
        all_valid = False

    # Check Publisher Agent
    publisher_result = verify_python_file(files["Publisher Agent"])
    if "PublisherAgent" in publisher_result.get("classes", []):
        print("✓ PublisherAgent class found")
    else:
        print("✗ PublisherAgent class NOT found")
        all_valid = False

    # Check __init__.py exports
    init_result = verify_python_file(files["__init__.py"])
    with open(files["__init__.py"]) as f:
        init_content = f.read()
        if "IteratorAgent" in init_content and "PublisherAgent" in init_content:
            print("✓ Both agents exported in __init__.py")
        else:
            print("✗ Agents NOT properly exported in __init__.py")
            all_valid = False

    print("-" * 70)

    # Summary
    print("\n" + "=" * 70)
    if all_valid:
        print("SUCCESS: All agents are properly structured and valid!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test with actual API calls")
        print("3. Integrate into the main workflow")
    else:
        print("ERRORS FOUND: Please fix the issues above")
        sys.exit(1)
    print("=" * 70)


if __name__ == "__main__":
    main()
