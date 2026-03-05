# 🤖 HR AI Agent — Role-Based Intelligent HR Assistant

> A smart, role-aware HR automation agent powered by **Google Gemini** and **Google Sheets**, built with **Streamlit**. The agent understands *who* is asking before deciding *what* it can do — making every action permission-driven and secure.

---

## 📌 What Is HR AI Agent?

**HR AI Agent** is an intelligent conversational assistant designed for Human Resource management. It uses **role-based access control (RBAC)** combined with **AI planning** to understand user queries and execute only the actions that the user's position allows.

Instead of a traditional HR dashboard where users manually click through menus, this agent lets users **talk naturally** — and the agent figures out what to do, who's asking, and whether it's allowed.

---

## 🧠 How It Works

```
User sends a query
       ↓
Agent identifies WHO is using the system (role/position)
       ↓
Agent PLANS the action based on the query
       ↓
Agent CHECKS if the role has permission for that action
       ↓
Agent EXECUTES or DENIES the action with a clear reason
```

### 🔐 Role-Based Permission System

The agent enforces a strict 3-tier permission model:

| Role | Permissions |
|------|------------|
| 👑 **Admin** | View any employee data · Update salaries · Change roles · Add new employees · Delete employees |
| 👔 **Senior HR** | View any employee data · Update *other* employees' salaries · Change *others'* roles · Cannot modify own record |
| 👤 **Employee** | View **only their own** data · Cannot update or change anything |

### 🔍 Real-World Examples

| Query | User Role | Agent Action |
|-------|-----------|--------------|
| *"Increase my salary by 10%"* | Senior HR | ❌ **Denied** — Senior HR cannot modify their own salary |
| *"Increase John's salary by 10%"* | Senior HR | ✅ **Executed** — Allowed to update other employees |
| *"Add a new employee named Sara"* | Admin | ✅ **Executed** — Admin has full write access |
| *"Delete employee ID 204"* | Employee | ❌ **Denied** — Employees have read-only access |
| *"What is my leave balance?"* | Employee | ✅ **Executed** — Employees can view their own data |
| *"Show me all employees in the sales department"* | Admin | ✅ **Executed** — Admin can view all records |

---

## 🗂️ Project Structure

```
HR_AI_Agent/
│
├── agents/
│   ├── hr_agent.py           # Main agent orchestration & role enforcement
│   ├── hr_agent_confiq.py    # Agent configuration & settings
│   ├── hr_agent_llm.py       # LLM integration & Gemini API calls
│   └── testing_agent.py      # Agent testing & debugging utilities
├── prompts/
│   └── llm_planner_prompt.py # System prompts & planner instructions for the agent
├── data_base_connection.py   # Google Sheets API connection & CRUD operations
├── streamlit_app.py          # Main Streamlit UI entry point
├── requirements.txt          # Python dependencies
├── .env                      # Your local environment variables (never commit this)
├── .env.example              # Environment variable template (safe to commit)
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/M-Tayyab-AI/HR_AI_Agent.git
cd HR_AI_Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Rename `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Then open `.env` and update:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_SHEET_ID=your_google_spreadsheet_id_here
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/your/service_account_credentials.json
```

### 4. Run the App

```bash
streamlit run streamlit_app.py
```

---

## 🔑 How to Get Your API Keys & Credentials

### 🟡 Step 1 — Get Your Google Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select an existing Google Cloud project or create a new one
5. Copy the generated API key
6. Paste it into your `.env` file as `GEMINI_API_KEY`

> ⚠️ Keep your API key private — never commit it to GitHub.

---

### 🟢 Step 2 — Get Your Google Spreadsheet ID

1. Go to [https://sheets.google.com](https://sheets.google.com)
2. Open or create the spreadsheet you want to use as the HR database
3. Look at the URL in your browser — it will look like:
   ```
   https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/edit
   ```
4. The long string between `/d/` and `/edit` is your **Spreadsheet ID**
   ```
   1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
   ```
5. Copy it and paste into your `.env` file as `GOOGLE_SHEET_ID`

---

### 🔵 Step 3 — Create a Google Service Account & Get Credentials

A **Service Account** allows the agent to read/write your Google Sheet programmatically.

#### A) Create the Service Account

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Select your project (or create one via **"New Project"**)
3. In the left sidebar, go to **APIs & Services → Library**
4. Search for **"Google Sheets API"** → Click **Enable**
5. Also search for **"Google Drive API"** → Click **Enable**
6. Now go to **APIs & Services → Credentials**
7. Click **"+ Create Credentials"** → Choose **"Service Account"**
8. Fill in:
   - **Service account name**: `hr-agent` (or anything you like)
   - **Service account ID**: auto-filled
   - Click **"Create and Continue"**
9. For the role, select **"Editor"** → Click **"Continue"** → **"Done"**

#### B) Download the JSON Credentials

1. In **APIs & Services → Credentials**, find your new service account
2. Click on its name to open it
3. Go to the **"Keys"** tab
4. Click **"Add Key"** → **"Create new key"**
5. Choose **JSON** → Click **"Create"**
6. A `.json` file will be downloaded automatically — keep this safe!
7. Place this file in your project folder
8. Update your `.env` with the path to this file:
   ```env
   GOOGLE_SERVICE_ACCOUNT_JSON=./your-service-account-file.json
   ```

#### C) Share Your Google Sheet with the Service Account

1. Open your Google Spreadsheet
2. Click the **"Share"** button (top right)
3. Copy the **service account email** from the JSON file (it looks like `hr-agent@your-project.iam.gserviceaccount.com`)
4. Paste it into the "Share" dialog
5. Set the role to **"Editor"**
6. Click **"Send"**

> ✅ The agent can now read and write to your spreadsheet.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| 🧠 **Google Gemini** | LLM powering the AI agent's reasoning and planning |
| 📊 **Google Sheets** | HR database (employees, roles, salaries) |
| 🌐 **Streamlit** | Web UI for interacting with the agent |
| 🔗 **Google Sheets API** | Programmatic read/write to spreadsheet |
| 🐍 **Python** | Backend logic, agent orchestration |

---

## 🙋 Author

**Muhammad Tayyab**
- GitHub: [@M-Tayyab-AI](https://github.com/M-Tayyab-AI)

---

## ⭐ If you find this useful, give it a star!