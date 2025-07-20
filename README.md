# 🧠 Multi Assistant Web App

A **multi-functional assistant platform** built using **Django**, **Langchain**, and **Groq LLM API**, designed to simplify day-to-day tasks like summarizing search results, extracting insights from YouTube videos, and providing coding assistance.

---

## 🚀 Features

- 🔍 **Search**: Ask any question or perform a search — the assistant returns intelligent, summarized answers using LLMs.
- 📺 **YouTube Video Insights**: Extracts meaningful summaries from YouTube videos using transcript analysis.
- 💻 **Coding Assistance**: Helps solve programming problems with natural language prompts.

---

## 🔐 Secure API Key Flow

To ensure user privacy, the application allows users to **enter their Groq API key** after logging in. This API key is **not stored** in any database or backend.

### 🔑 Groq API Setup
1. Go to the [Groq Developer Portal](https://console.groq.com/developer).
2. Sign up or log in.
3. Navigate to the **"API Keys"** section.
4. Generate a **free API key**.
5. Enter your API key on the app dashboard to start using the assistant.

---

## 🛠️ Technologies Used

- **Backend**: Django (Python)
- **LLM Framework**: LangChain
- **LLM Provider**: Groq API
- **Environment Management**: `.env` for secure variables
- **Deployment**: Docker (optional but recommended)

---

## 🐳 Docker Support

The app can be easily containerized using Docker. A Docker image includes all required dependencies for smooth deployment.

### Docker Setup
```bash
# Build Docker image
docker build -t multi-assistant .

# Run container
docker run -p 8000:8000 multi-assistant
```

---

## 🌐 Deployment Notes

Before deploying the application, make sure to collect all static files to ensure the frontend renders correctly:

```bash
python manage.py collectstatic
