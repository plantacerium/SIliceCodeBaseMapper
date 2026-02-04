# 💠 Silice AI Native Codebase Mapper

**Silice Codebase Mapper** is a local, AI-powered documentation and dependency mapping suite. It transforms a messy codebase into a **Structured Knowledge Graph** specifically optimized for ingestion by Large Language Models (LLMs) via Ollama.

By breaking down code into atomic JSON "neurons" and a central "synapse" (`index.json`), it allows AI agents to understand your project's architecture, intent, and impact without exceeding context windows.

---

## 🚀 Features

* **Atomic Ingestion**: Generates a unique JSON map for every source file.
* **AI Enrichment**: Uses **Ollama + Instructor** to extract logic summaries and conceptual relations.
* **Static & Dynamic Analysis**: Combines Python's `ast` for reliable structure with LLMs for "intent" analysis.
* **Impact Analysis**: Query-tool to see how changing one function ripples through the graph.
* **AI Bridge**: A RAG (Retrieval-Augmented Generation) chat interface to talk to your code locally.

---

## 🛠️ Installation

1. **Requirement**: Ensure you have [Ollama](https://ollama.com/) installed and running.
2. **Model**: Pull a compatible model (Llama 3 is recommended):
```bash
ollama pull llama3

```


3. **Dependencies**:
```bash
pip install ollama instructor pydantic

```



---

## 📂 The Core "Trinity"

### 1. The Mapper (`silice_file_mapper.py`)

The "Worker." It crawls your directories, performs static analysis, and asks the AI to document the logic of every file.

* **Output**: `silice_output/*.json` and `index.json`.
* **Usage**:
```bash
python silice_file_mapper.py ./src ./lib

```



### 2. The Query Tool (`silice_query.py`)

The "Analyst." Use this to traverse the graph and check dependencies.

* **Usage**:
```bash
# See what depends on a specific class or function
python silice_query.py --impact AuthService

# Get a quick AI-generated summary of a file
python silice_query.py --info models/user.py

```



### 3. The Bridge (`silice_bridge.py`)

The "Interface." An interactive chat that uses the generated JSON maps as a local brain to answer complex architectural questions.

* **Usage**:
```bash
python silice_bridge.py

```



---

## 📊 Data Schema

The system uses Pydantic to enforce strict adherence to the **Silice Protocol**. Every file is mapped into a `FileNode`:

| Field | Description |
| --- | --- |
| **`file_path`** | Absolute location for reference. |
| **`functions`** | List of names, signatures, and AI-summarized logic. |
| **`dependencies`** | Graph-edges (imports, calls, inheritance). |
| **`summary`** | A high-level overview of the file's "Reason for Being." |

---

## 🛠️ Workflow

1. **Scan**: Run the Mapper to build your JSON library.
2. **Index**: The `index.json` creates a master map of all file relations.
3. **Consult**: Use the Bridge or Query tool to navigate the project without ever reading the raw source code.

---

## ⚠️ Notes

* **Context Control**: This suite is designed to avoid "Context Bloat." The Bridge only feeds the AI the specific JSON maps relevant to your current question.
* **Performance**: For faster mapping, you can edit the script to use `model="phi3"` or `model="mistral"` in the Ollama client.

---
<div align="center">

**Made with ❤️ and ☕ by the Plantacerium**

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/plantacerium)

⭐ **Star us on GitHub** ⭐
</div>
