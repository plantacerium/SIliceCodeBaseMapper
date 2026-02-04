import os
import ast
import json
import argparse
import instructor
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from ollama import Client

# --- Silice Protocol v3 Models ---

class Dependency(BaseModel):
    source: str
    target: str
    type: str = Field(..., description="e.g., 'import', 'inheritance', 'call'")

class FunctionMap(BaseModel):
    name: str
    signature: str
    docstring: Optional[str]
    calls: List[str] = Field(default_factory=list)
    logic_summary: str = Field(..., description="AI generated summary of the function's purpose")

class FileNode(BaseModel):
    file_name: str
    file_path: str
    functions: List[FunctionMap]
    classes: List[str]
    dependencies: List[Dependency]
    summary: str = Field(..., description="High-level overview of the file's role in the system")

# --- AI Instructor Setup ---

# Patching Ollama with Instructor
client = instructor.patch(Client())

def analyze_with_ollama(content: str, static_info: dict) -> FileNode:
    """Uses Ollama to generate the Silice Protocol compliant JSON."""
    prompt = f"""
    Analyze this code. 
    Static Analysis Found: {json.dumps(static_info)}
    
    Code Content:
    {content}
    
    Generate a full map of logic, function purposes, and internal dependencies.
    """
    
    return client.chat.completions.create(
        model="gemma3:4B",
        messages=[{"role": "user", "content": prompt}],
        response_model=FileNode,
    )

# --- Processing Logic ---

def get_static_metadata(file_path: Path):
    """AST check for basic structure."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return None
        
    return {
        "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
        "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
    }

def process_single_file(file_path: Path, output_dir: Path, master_index: dict):
    """Analyzes a single file and saves its unique JSON."""
    print(f"[*] Analyzing: {file_path}")
    
    static_info = get_static_metadata(file_path)
    if not static_info:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Get structured AI data
    analysis = analyze_with_ollama(content, static_info)
    analysis.file_name = file_path.name
    analysis.file_path = str(file_path.absolute())

    # Save individual JSON
    # Replacing separators to create a flat output directory
    safe_name = str(file_path).replace(os.sep, "_") + ".json"
    output_file = output_dir / safe_name
    
    with open(output_file, "w") as f:
        f.write(analysis.model_dump_json(indent=4))

    # Update Master Index
    master_index["graph_nodes"].append({
        "file": str(file_path),
        "map_ref": str(output_file),
        "summary": analysis.summary
    })
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description="Silice File-to-JSON Mapper")
    parser.add_argument("paths", nargs="+", help="Folders or Files to analyze")
    args = parser.parse_args()

    output_dir = Path("silice_output")
    output_dir.mkdir(exist_ok=True)

    master_index = {"project_root": os.getcwd(), "graph_nodes": []}
    
    files_to_process = []
    for p in args.paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".py":
            files_to_process.append(path)
        elif path.is_dir():
            files_to_process.extend(path.glob("**/*.py"))

    for file in files_to_process:
        if "__pycache__" in str(file): continue
        process_single_file(file, output_dir, master_index)

    # Save the root index.json
    with open("index.json", "w") as f:
        json.dump(master_index, f, indent=4)
    
    print(f"\n[!] Done. Individual maps are in '{output_dir}/'. Global index is in 'index.json'.")

if __name__ == "__main__":
    main()
