# 🤖 FlareBot
[![Flare](https://img.shields.io/badge/flare-network-e62058.svg?logo=data:image/svg+xml;base64,...&colorA=FFFFFF)](https://dev.flare.network/)

> 🏆 **2nd Place Winner** at the **Google x Flare Verifiable AI Hackathon**

FlareBot is an autonomous AI agent designed to provide **24/7 support** for the Flare Network Discord server. Built with a real-time Retrieval-Augmented Generation (RAG) pipeline and deployed inside a secure Trusted Execution Environment, FlareBot is the most robust and secure Discord bot for dev and user support.

---

## 🚀 Why FlareBot?

- **⚡ Always-On Support**  
  Answers technical and user questions instantly, day or night.

- **📚 Live Knowledge Updates**  
  Dynamically learns from new Discord messages by support staff, no redeploy needed.

- **🧠 Built for Flare**  
  Fine-tuned using Flare Developer Docs and real support chat logs for maximum relevance.

- **🔧 Fully Customizable**  
  Staff can expand FlareBot’s knowledge base on the fly and restrict topics with `!norag`.

- **🛡️ Secure by Design**  
  Deployed in a **TEE (Trusted Execution Environment)** using **Google Confidential Space** for privacy-preserving AI.

---

## 🛠 Tech Stack

| Layer         | Tech                                                             |
|---------------|------------------------------------------------------------------|
| Backend       | Python 3.12, FastAPI, Gemini API                                 |
| Retrieval     | Qdrant (Vector Search DB)                                        |
| RAG Pipeline  | Live Discord message ingestion + Flare doc embeddings            |
| Infra         | Docker, GCP Confidential Space (AMD SEV), uv                    |

---

## 🧠 How It Works

1. **Ingests Flare docs** and real-time Discord messages from support staff.
2. **Indexes using Qdrant** for fast embedding and retrieval.
3. **Gemini API** reformulates user questions, retrieves context, and responds.
4. **RAG is live**: the bot retrains itself whenever staff chat.
5. Staff can issue commands like `!norag` to restrict content live.

---

## 📸 Preview Example

**FlareBot learning live from support staff in Discord**  
> New support messages are automatically added to the knowledge base in real-time. 🔁

![FlareBot Live Learning Preview](https://github.com/user-attachments/assets/6389fe1b-49d2-4bbf-b84a-1b8f430c74fa)



