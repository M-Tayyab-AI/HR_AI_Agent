# HR AI Agent 🤖

An intelligent **Role-Based HR AI Agent** that understands user queries, identifies the user's role in the organization, and performs actions accordingly.

This project demonstrates how **AI agents can enforce HR policies automatically** by combining **LLMs, role-based permissions, and automated action planning**.

---

# 🚀 Project Overview

The **HR AI Agent** acts like a virtual HR assistant.  
A user sends a query, and the agent:

1. Identifies **who is using the system** (their role or position).
2. **Analyzes the request** using an AI model.
3. **Plans an action** based on company HR rules.
4. **Executes or denies the action** depending on the user's permissions.

The system ensures that **users can only perform actions allowed by their role**.

---

# 🧠 How It Works

### Step 1 User Query
A user submits a query such as:

- "Increase my salary"
- "Show my employee data"
- "Add a new employee"
- "Change employee role"

---

### Step 2 Role Detection
The agent checks **who is using the system** and determines their role:

Examples:
- **Admin**
- **Senior HR**
- **Employee**

---

### Step 3 Action Planning
The AI agent analyzes the query and **creates a plan** to perform the action based on role permissions.

---

### Step 4 Permission Enforcement
The system checks whether the user is allowed to perform that action.

Examples:

#### Admin
Admins have **full access**.

They can:
- Add new employees
- Delete employees
- Update employee salary
- Change employee roles
- View employee data

---

#### Senior HR
Senior HR has **limited administrative access**.

They can:
- Increase employee salaries
- View employee data

They **cannot**:
- Increase their own salary

---

#### Employee
Regular employees have **read-only access**.

They can:
- View their own data

They **cannot**:
- Modify their salary
- Change roles
- Modify other employees' data

---

# ⚙️ Tech Stack

- **Python**
- **Streamlit**
- **Google Gemini API**
- **Google Service Account**
- **LLM-based Agent Planning**

---

# 📦 Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/M-Tayyab-AI/HR_AI_Agent.git
cd HR_AI_Agent
```
## 2️⃣ Clone the Repository
```bash
pip install -r requirements.txt
```
## 3️⃣ Configure Environment Variables
```bash
cp .env.example .env
```
Then update the .env file with:

GEMINI_API_KEY=your_api_key_here

Create a Google Service Account:
1. Go to Google Cloud Console.
2. Create a Service Account.
3. Download the JSON credentials.

Paste the credentials inside the .env file as instructed in .env.example

## ▶️ Running the Application
Start the Streamlit app:
```bash
streamlit run streamlit_app.py
```
## 🎯 Purpose of the Project
This project showcases how AI agents can be used in real-world enterprise systems to:
1. Automate HR workflows
2. Enforce company policies
3. Perform intelligent decision making
4. Improve employee self-service systems

## 👨‍💻 Author
### Muhammad Tayyab
### AI Engineer
### Focused on LLMs, AI Agents, and Automation Systems

## GitHub:
https://github.com/M-Tayyab-AI