

# 🧠 AI Daily Planner

A local-first, AI-powered daily planner that transforms messy brain dumps into a prioritized, time-blocked schedule. 

Built with **Next.js**, **Vercel AI SDK**, **Groq**, and **Ollama**, this app demonstrates how to build reliable AI features using a "Hybrid" architecture: using LLMs for judgment, and deterministic code for constraints.

## ✨ Features

- **Brain Dump Extraction:** Type a messy paragraph, and the AI extracts structured tasks with priorities, time estimates, and tags.
- **Goal Decomposition:** Turn vague weekly goals (e.g., "Learn React") into 1-5 concrete, actionable tasks.
- **Hybrid Scheduling:** The AI orders tasks based on priority and context, while a deterministic algorithm calculates the exact clock times, inserting lunch and focus breaks.
- **Focus Mode:** Click "Focus" on any scheduled task to start a built-in countdown timer.
- **Grounded Reviews:** The AI compares your *planned* schedule against your *actual* completions to provide factual, non-generic advice for tomorrow.
- **Bring Your Own Key (BYOK):** Zero API costs for the host. Users simply paste their own Groq API key in the UI.
- **Local-First:** All data is stored in your browser's `localStorage`. No database, no user accounts, complete privacy.

## 🏗️ Architecture: LLM for Judgment, Code for Constraints

Most AI scheduling apps fail because they ask the LLM to calculate time blocks. LLMs are bad at arithmetic and will happily schedule 11 hours of work into an 8-hour day.

This app solves that by splitting the brain in two:
1. **The AI (`lib/ai/propose.ts`):** Handles *judgment*. It receives the tasks and returns an ordered array of task IDs, batching similar tasks and prioritizing high-impact work.
2. **The Scheduler (`lib/scheduler.ts`):** Handles *math*. It takes the AI's order and places them into a grid, calculating start/end times, inserting breaks every 90 minutes, and ensuring tasks don't overlap.

If the AI fails or hallucinates, the scheduler seamlessly falls back to a deterministic priority sort. 

## 🛠️ Tech Stack

- **Framework:** [Next.js 16](https://nextjs.org/) (App Router)
- **AI Integration:** [Vercel AI SDK](https://sdk.vercel.ai/docs)
- **Structured Output:** [Zod](https://zod.dev/)
- **Cloud LLM Provider:** [Groq](https://groq.com/) (Default: `openai/gpt-oss-120b`)
- **Local LLM Provider:** [Ollama](https://ollama.com/) (Default: `qwen3:8b`)

---

## 🚀 Getting Started

### Prerequisites

- Node.js v22 or higher
- A free [Groq API Key](https://console.groq.com/) (No credit card required)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/planner.git
   cd planner
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open the app:**
   Navigate to `http://localhost:3000` in your browser.

### Configuring the AI

1. Scroll down to the **AI Settings (BYOK)** section at the bottom of the app.
2. Paste your Groq API key (`gsk_...`). It is stored securely in your browser's local storage and only sent to your local Next.js server to make the API calls.

---

## 🖥️ Running Fully Offline (Ollama)

If you want zero API costs and complete offline privacy:

1. Install [Ollama](https://ollama.com/) on your machine.
2. Pull the recommended model:
   ```bash
   ollama pull qwen3:8b
   ```
3. In the app's `AI settings`, change the provider from `Groq` to `Ollama`. 
4. The app will now route all AI requests to your local machine on `127.0.0.1:11434`.

---

## 📁 Project Structure

```text
├── app/
│   ├── api/          # Next.js Route Handlers (Backend)
│   │   ├── extract/  # Brain dump -> JSON tasks
│   │   ├── goal/     # Big goals -> Concrete actions
│   │   ├── plan/     # AI ordering + Deterministic scheduling
│   │   └── review/   # Planned vs Actual reflection
│   ├── page.tsx      # Main React frontend (UI)
│   └── globals.css   # Glassmorphism / Atmospheric styling
├── lib/
│   ├── ai/           # AI Prompts, Zod schemas, and Provider configs
│   ├── plan/         # Logic to merge AI proposals with deterministic sorts
│   ├── scheduler.ts  # The core math engine (time blocks, breaks, lunch)
│   └── types.ts      # Shared TypeScript interfaces
```
