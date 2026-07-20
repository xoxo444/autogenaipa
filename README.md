# AutoGen Personal AI Assistant

A modular, multi-agent AI personal assistant built using Python and Microsoft's AutoGen framework. The assistant intelligently plans user requests, executes tasks through specialized agents, maintains long-term semantic memory using FAISS, and integrates with external services such as Gmail, Google Calendar, Weather APIs, Google Drive, and the local filesystem.

---

## Features

- Multi-Agent Architecture
- Dynamic Task Planning
- DAG-Based Workflow Execution
- Persistent Long-Term Memory (FAISS)
- Semantic Search using Hugging Face Embeddings
- Conversation History Management
- Google Calendar Integration
- Gmail Integration
- Weather Agent
- Google Drive MCP Client
- Filesystem MCP Client
- Modular & Extensible Agent Framework

---

## Architecture

```text
                    User
                      │
                      ▼
             Personal Assistant
                      │
          Dynamic Task Planner
                      │
                      ▼
               DAG Executor
        ┌─────────┼──────────┐
        ▼         ▼          ▼
   Weather     Gmail     Calendar
     Agent      Agent       Agent
        │         │          │
        └─────────┼──────────┘
                  ▼
          Response Aggregation
                  │
                  ▼
         Conversation Manager
                  │
                  ▼
             Memory Manager
                  │
                  ▼
      FAISS Vector Store + Metadata
                  │
                  ▼
       Hugging Face Embeddings
```

---

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Framework | Microsoft AutoGen |
| Memory | FAISS |
| Embeddings | Hugging Face (`all-MiniLM-L6-v2`) |
| APIs | Gmail API, Google Calendar API, Weather API |
| Authentication | Google OAuth 2.0 |
| AI Models | OpenAI-compatible LLMs |
| Data Storage | JSON + FAISS Index |

---

## Project Structure

```
.
├── agents/
├── auth/
├── core/
├── memory/
├── mcp_clients/
├── tools/
├── app.py
└── requirements.txt
```

---

## Memory System

The assistant implements persistent semantic memory using FAISS.

- Stores conversation memories as vector embeddings
- Retrieves relevant memories using cosine similarity
- Maintains metadata separately for efficient lookup
- Uses Hugging Face sentence-transformer embeddings
- Persists memory across sessions

---

## Supported Agents

- Weather Agent
- Gmail Agent
- Calendar Agent
- Google Drive Agent
- Filesystem Agent

The architecture is modular, allowing additional agents to be added with minimal changes.

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/xoxo444/autogenaipa.git
cd autogenaipa
```

### Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file and add the required API keys.

Example:

```env
OPENAI_API_KEY=
HF_TOKEN=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Run

```bash
python app.py
```

---

## Future Improvements

- Web Interface
- Voice Interaction
- Streaming Responses
- Memory Importance Scoring
- Memory Deduplication
- Additional Productivity Agents
- Desktop Automation

---

## Author

**Jiya Tiwari**

