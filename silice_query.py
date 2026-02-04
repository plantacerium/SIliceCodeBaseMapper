import json
from pathlib import Path
import argparse

class SiliceGraph:
    def __init__(self, index_path: str = "index.json"):
        self.index_path = Path(index_path)
        if not self.index_path.exists():
            raise FileNotFoundError("Run the mapper first to generate index.json!")
        
        with open(self.index_path, "r") as f:
            self.index = json.load(f)
        
        self.nodes = {}
        self._load_all_maps()

    def _load_all_maps(self):
        """Loads all individual file JSONs into memory."""
        for entry in self.index["graph_nodes"]:
            map_path = Path(entry["map_ref"])
            if map_path.exists():
                with open(map_path, "r") as f:
                    self.nodes[entry["file"]] = json.load(f)

    def find_dependents(self, target_name: str):
        """Finds which files depend on a specific function, class, or file."""
        print(f"\n--- Impact Analysis for: **{target_name}** ---")
        impacted = []

        for file_path, data in self.nodes.items():
            # Check dependencies list
            for dep in data.get("dependencies", []):
                if target_name in dep["target"]:
                    impacted.append((file_path, dep["type"]))
            
            # Check function calls inside the AI-generated maps
            for func in data.get("functions", []):
                if any(target_name in call for call in func.get("calls", [])):
                    impacted.append((file_path, f"function call in {func['name']}"))

        if not impacted:
            print("No direct dependents found in the current graph.")
        else:
            for file, reason in set(impacted):
                print(f"  [!] Potential Impact: **{file}** ({reason})")

    def show_summary(self, file_query: str):
        """Quickly retrieve the AI summary of a file's logic."""
        for file_path, data in self.nodes.items():
            if file_query in file_path:
                print(f"\n### Logic Summary for {file_path}:")
                print(f"> {data.get('summary', 'No summary available.')}")
                print("\n**Functions:**", ", ".join([f["name"] for f in data.get("functions", [])]))

# --- CLI Implementation ---

def main():
    parser = argparse.ArgumentParser(description="Query the Silice Codebase Graph")
    parser.add_argument("--impact", type=str, help="Search for what depends on this component")
    parser.add_argument("--info", type=str, help="Get the AI summary of a specific file")
    args = parser.parse_args()

    try:
        graph = SiliceGraph()
        if args.impact:
            graph.find_dependents(args.impact)
        elif args.info:
            graph.show_summary(args.info)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
