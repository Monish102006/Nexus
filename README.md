# NEXUS --- Autonomous Mission Control

NEXUS turns a natural-language objective into a coordinated multi-agent
workflow. It produces a structured plan, drafts a Telegram announcement,
and **waits for human approval before sending anything externally**.

**Example mission:** "Plan a deployment for my mobile application."

## What is implemented

  -----------------------------------------------------------------------
  Area                                Status
  ----------------------------------- -----------------------------------
  FastAPI backend + SQLite            Implemented
  persistence                         

  Custom orchestrator + 3 specialised Implemented
  agents                              

  Research → Planning → Communication Implemented; agent outputs are
  hand-off                            passed between agents

  Human approval workflow (approve /  Implemented
  reject / duplicate guard)           

  React + Vite + Tailwind dashboard   Implemented

  Telegram bot (polling, commands,    Configured; live Telegram mission
  mission intake)                     intake tested

  Groq LLM integration through an     Configured; verify runtime status
  OpenAI-compatible API               in `/api/health`

  Approved Telegram delivery          Requires an end-to-end approval
                                      test before claiming live delivery

  Demo mode when no LLM credentials   Supported
  exist                               

  Activity timeline from backend      Implemented
  events                              
  -----------------------------------------------------------------------

> **Current integration evidence:** A real mission was submitted through
> Telegram and NEXUS returned a mission with a deployment plan and a
> draft announcement awaiting approval. This confirms Telegram mission
> intake. Do not describe outbound Telegram delivery as live-tested
> unless you have approved a draft and verified that the message arrived
> in Telegram.

## How NEXUS works

1.  A user submits an objective through the web dashboard or Telegram.
2.  The orchestrator runs three specialised agents in sequence:
    -   **Research Agent:** identifies requirements, constraints,
        missing information and risks.
    -   **Planning Agent:** creates tasks, priorities, deadlines and
        dependencies.
    -   **Communication Agent:** drafts a Telegram announcement and
        action payload. It does not send messages.
3.  The mission, tasks and agent outputs are persisted in SQLite.
4.  The draft enters the approval queue.
5.  A human approves or rejects the draft in the dashboard.
6.  Only the approval workflow can initiate the outbound Telegram
    action.

``` text
Web dashboard ───────┐
                     ├──> FastAPI API ──> Orchestrator
Telegram bot ────────┘                       |
                                  ┌──────────┼──────────┐
                                  v          v          v
                              Research   Planning  Communication
                                Agent      Agent       Agent
                                  |          |           |
                                  └──────────┴───────────┘
                                             |
                                      Pending approval
                                             |
                                      Human decision
                                       /         \
                                  Reject         Approve
                                    |               |
                                  Stop        Telegram Bot API
```

The communication agent **never sends**. It only creates a draft. The
approval service is the controlled path to an outbound action.

### Persistence

The orchestrator stores:

-   `missions` --- objective, status, summary and source
-   `tasks` --- title, priority, deadline and dependency
-   `agent_results` --- structured output from each agent
-   `approvals` --- draft content, status, target chat and message ID
-   `activities` --- execution timeline events

## Project structure

``` text
Promptwars/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── research.py
│   │   │   ├── planning.py
│   │   │   ├── communication.py
│   │   │   └── orchestrator.py
│   │   ├── core/llm.py
│   │   ├── integrations/telegram_bot.py
│   │   ├── services/
│   │   │   ├── mission_service.py
│   │   │   └── approval_service.py
│   │   ├── api/routes.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/test_flow.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Requirements

-   Python 3.10+
-   Node.js and npm
-   A Groq API key for live LLM calls
-   A Telegram bot token for Telegram integration

## Run NEXUS (Windows PowerShell)

### 1. Backend

``` powershell
cd E:\Development\Promptwars\backend

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Copy-Item .env.example .env
# Edit backend/.env and add your credentials.

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend endpoints:

-   API: http://127.0.0.1:8000
-   Swagger: http://127.0.0.1:8000/docs
-   Health: http://127.0.0.1:8000/api/health

The SQLite database is created automatically at `backend/nexus.db`.
Delete that file to reset locally stored missions and related data.

### 2. Frontend

Open a second PowerShell window:

``` powershell
cd E:\Development\Promptwars\frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173.

If PowerShell blocks `Activate.ps1`, you can skip virtual-environment
activation and invoke `.\.venv\Scripts\python.exe` directly, as shown
above.

## Configuration

Create `backend/.env` using the following variables. Keep real
credentials in `.env` only; **never commit `.env` or paste secrets into
screenshots, issues or source control**.

``` dotenv
DATABASE_URL=sqlite:///./nexus.db

# Groq (OpenAI-compatible API)
LLM_API_KEY=your_groq_api_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
LLM_TIMEOUT=60
DEMO_MODE=false

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_ALLOWED_CHAT_IDS=your_allowed_chat_id
TELEGRAM_DEFAULT_CHAT_ID=your_default_chat_id

# Frontend origin
CORS_ORIGINS=http://127.0.0.1:5173
```

The configured model name must be available to your Groq account. Check
the Groq console for currently supported models if the configured model
is unavailable.

### LLM mode

-   With a valid `LLM_API_KEY` and `DEMO_MODE=false`, agents use the
    configured OpenAI-compatible LLM endpoint.
-   If the key is missing, demo mode is enabled, or an LLM request
    fails, the application may use its deterministic fallback, depending
    on the failure path. Check the backend logs and `/api/health` to
    confirm the actual runtime mode.
-   Do not assume that setting environment variables alone proves live
    LLM use; verify the health response and inspect a newly generated
    mission.

No credentials are hardcoded, and API keys should not be exposed to the
browser.

## Telegram setup

1.  Create a Telegram bot using [@BotFather](https://t.me/BotFather) and
    copy its token.
2.  Add the token to `TELEGRAM_BOT_TOKEN` in `backend/.env`.
3.  Configure `TELEGRAM_ALLOWED_CHAT_IDS` with the chat IDs permitted to
    interact with the bot.
4.  Configure `TELEGRAM_DEFAULT_CHAT_ID` as the destination for
    approvals initiated from the web dashboard, if required by your
    workflow.
5.  Restart the backend.
6.  Open the bot in Telegram and send `/start`.
7.  Send a natural-language objective. The bot submits it to the same
    orchestrator used by the dashboard and replies with the mission
    result and draft.
8.  Review the draft in the NEXUS dashboard. Approve only if the content
    and recipient are correct; otherwise reject it.

Commands:

-   `/start` --- initialise interaction with the bot
-   `/help` --- show usage instructions
-   Any plain-language objective --- create a mission

### Telegram safety and delivery notes

-   `TELEGRAM_ALLOWED_CHAT_IDS` restricts who can submit missions and
    receive replies. Configure it rather than leaving the bot open to
    everyone.
-   Missions submitted through Telegram can retain the originating chat
    for replies and delivery.
-   For approvals initiated from the web dashboard, configure
    `TELEGRAM_DEFAULT_CHAT_ID` when needed. The application should not
    guess a destination when multiple chats are known.
-   The health endpoint exposes a count of known Telegram chats, not
    their IDs.
-   If Telegram is not configured, the application may record an
    approval without delivering a message; check the execution
    note/status rather than assuming delivery.
-   **Live mission intake has been tested. Verify an approved outbound
    message separately before claiming that live delivery has been
    tested.**

## Demo walkthrough

1.  Start the backend and frontend.
2.  Confirm the LLM and Telegram statuses in the dashboard or
    `/api/health`.
3.  Submit an objective such as:\
    `Plan a deployment for my mobile application.`
4.  Open the mission in the dashboard.
5.  Inspect the Research, Planning and Communication agent outputs and
    review the generated tasks, timeline and risks.
6.  Open the approval queue and review the proposed Telegram
    announcement.
7.  Reject an unsuitable draft, or approve a correct draft.
8.  If approving, verify that the Telegram message actually arrives and
    that the mission activity records the delivery result.

## API endpoints

  -------------------------------------------------------------------------------
  Method                  Path                            Description
  ----------------------- ------------------------------- -----------------------
  `POST`                  `/api/missions`                 Create and orchestrate
                                                          a mission

  `GET`                   `/api/missions`                 List missions

  `GET`                   `/api/missions/{id}`            Retrieve full mission
                                                          details

  `GET`                   `/api/agents`                   Agent metadata and run
                                                          statistics

  `GET`                   `/api/approvals`                List approvals
                                                          (`?status=pending`)

  `POST`                  `/api/approvals/{id}/approve`   Approve and attempt
                                                          delivery

  `POST`                  `/api/approvals/{id}/reject`    Reject; does not send

  `GET`                   `/api/activity`                 Retrieve activity
                                                          timeline

  `GET`                   `/api/health`                   Check application, LLM
                                                          and Telegram status
  -------------------------------------------------------------------------------

## Tests

Run the backend flow tests:

``` powershell
cd E:\Development\Promptwars\backend
.\.venv\Scripts\python.exe -m unittest tests.test_flow -v
```

The project test suite is intended to verify:

1.  The pipeline produces connected agent outputs, tasks and a pending
    approval.
2.  Approval delivers at most once, records the message ID when delivery
    succeeds, and blocks duplicate approval attempts.
3.  Rejection does not trigger delivery and prevents later approval.

Run the tests in your current environment and report the actual result.
Do not claim that tests pass unless they have been executed
successfully.

## Screenshots

Add current screenshots captured from your running application.
Suggested files:

  -----------------------------------------------------------------------
  View                                Suggested artifact
  ----------------------------------- -----------------------------------
  Dashboard overview                  `nexus-dashboard.png`

  Approval queue                      `nexus-approvals.png`

  Agent fleet                         `nexus-agents.png`

  Mission details/list                `nexus-missions.png`

  Post-approval delivery result (only `nexus-after-approve.png`
  after a real test)                  
  -----------------------------------------------------------------------

Do not include API keys, Telegram bot tokens, chat IDs or other secrets
in screenshots.

## Current scope and limitations

-   NEXUS creates plans and drafts communications; tasks are **planned,
    not automatically executed**.
-   The Research Agent works from the submitted objective and available
    application context. It should not be described as web research or
    source-backed research unless those capabilities are added and
    verified.
-   The dashboard uses periodic polling rather than WebSockets.
-   LLM output depends on provider availability, model access, prompt
    quality and response parsing. Failed or malformed responses may use
    a fallback; check logs and runtime status.
-   Telegram mission intake has been exercised with a real bot. Outbound
    delivery should be described as verified only after an approved
    message has been received in the intended Telegram chat.
-   The approval workflow is a human-in-the-loop safeguard: the
    Communication Agent drafts, while a human decides whether the
    proposed external action should proceed.

------------------------------------------------------------------------

**NEXUS --- From objectives to coordinated action, with human approval
in control.**
