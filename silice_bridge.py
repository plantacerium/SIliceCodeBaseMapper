import json
import os
from pathlib import Path
import instructor
from ollama import Client
from typing import List

# --- Setup ---
client = instructor.patch(Client())
INDEX_FILE = "index.json"

class SiliceBridge:
    def __init__(self):
        if not Path(INDEX_FILE).exists():
            raise FileNotFoundError("Please run the mapper script first to generate index.json.")
        
        with open(INDEX_FILE, "r") as f:
            self.index = json.load(f)
        
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Finds the most relevant JSON nodes based on the user query."""
        # Simple keyword matching against summaries for retrieval
        scores = []
        query_words = set(query.lower().split())

        for node in self.index["graph_nodes"]:
            summary = node.get("summary", "").lower()
            file_name = node.get("file", "").lower()
            
            # Basic overlap score
            score = sum(1 for word in query_words if word in summary or word in file_name)
            if score > 0:
                scores.append((score, node["map_ref"]))

        # Sort by score and take top_k
        scores.sort(key=lambda x: x[0], reverse=True)
        relevant_maps = [s[1] for s in scores[:top_k]]
        
        context_data = []
        for map_path in relevant_maps:
            if Path(map_path).exists():
                with open(map_path, "r") as f:
                    context_data.append(f.read())
        
        return "\n---\n".join(context_data)

    def chat(self):
        print("--- Silice Protocol v3: AI Bridge Active ---")
        print("Ask anything about your codebase (type 'exit' to quit).")
        
        history = []
        
        while True:
            user_input = input("\n[User]: ")
            if user_input.lower() in ["exit", "quit"]: break
            
            # 1. Retrieve relevant JSON maps
            context = self.retrieve_context(user_input)
            
            # 2. Augment the prompt
            system_prompt = (
                "You are an expert software architect. You have access to structured JSON maps "
                "of a codebase. Use the following context to answer the user's questions accurately. "
                "Context represents file relations, functions, and logic summaries.\n\n"
                f"CODEBASE CONTEXT:\n{context}"
            )
            
            # 3. Generate response using Ollama
            messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_input}]
            
            print("\n[Silice AI]: ", end="", flush=True)
            response = ""
            
            # Using standard stream for better UX
            stream = Client().chat(
                model="llama3",
                messages=messages,
                stream=True,
            )
            
            for chunk in stream:
                content = chunk['message']['content']
                print(content, end="", flush=True)
                response += content
            
            print()
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    bridge = SiliceBridge()
    bridge.chat()
