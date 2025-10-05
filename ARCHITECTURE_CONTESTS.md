# Contest Management System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│                     http://localhost:3000                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 │ (credentials: include)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Flask API)                         │
│                     http://localhost:5000                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Contest Endpoints                           │  │
│  │  - POST   /api/contests           (Create - FR3.1/3.2)   │  │
│  │  - POST   /api/contests/:id/run   (Execute - FR3.3/3.4)  │  │
│  │  - GET    /api/contests           (List)                 │  │
│  │  - GET    /api/contests/:id       (Details - FR3.3)      │  │
│  │  - GET    /api/agents/:id/record  (Records - FR3.4)      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Game Execution Engine                          │  │
│  │  - Load agent classes dynamically                         │  │
│  │  - Execute game loop                                      │  │
│  │  - Track every action (FR3.3)                             │  │
│  │  - Determine winner                                       │  │
│  │  - Update records (FR3.4)                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ SQL Queries
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   contests   │   │contest_actions│  │agent_records │        │
│  ├──────────────┤   ├──────────────┤   ├──────────────┤        │
│  │ contest_id   │   │ action_id    │   │ record_id    │        │
│  │ name         │   │ contest_id   │   │ agent_id     │        │
│  │ game         │   │ move_number  │   │ wins         │        │
│  │ agent1_id    │   │ agent_id     │   │ losses       │        │
│  │ agent2_id    │   │ action_data  │   │ draws        │        │
│  │ winner_id    │   │ board_state  │   └──────────────┘        │
│  │ status       │   └──────────────┘                            │
│  │ created_at   │                                                │
│  │ completed_at │                                                │
│  └──────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Contest Lifecycle Flow

```
1. CREATE CONTEST (FR3.1 / FR3.2)
   ┌─────────────────────────────────────┐
   │ Admin/Tutor clicks "Create Contest" │
   └─────────────────────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────┐
   │   Choose Manual or Auto-Match?      │
   └─────────────────────────────────────┘
          │                    │
     Manual                Auto-Match
          │                    │
          ▼                    ▼
   ┌─────────────┐      ┌──────────────┐
   │Select Agents│      │Random Select │
   └─────────────┘      └──────────────┘
          │                    │
          └──────────┬─────────┘
                     ▼
           ┌──────────────────┐
           │POST /api/contests│
           └──────────────────┘
                     │
                     ▼
           ┌──────────────────┐
           │ Contest Created  │
           │ Status: pending  │
           └──────────────────┘


2. RUN CONTEST (FR3.3 / FR3.4)
   ┌──────────────────────────────┐
   │ Admin clicks "Run" button    │
   └──────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ POST /api/contests/:id/run             │
   └────────────────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ Load Agent Classes from File System    │
   │ - Agent 1: games/.../group1/agent.py   │
   │ - Agent 2: games/.../group2/agent.py   │
   └────────────────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │     Initialize Game Instance           │
   │ GameClass(agent1_instance, agent2)     │
   └────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  Game Loop      │
        │  (Modified)     │
        └─────────────────┘
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
   ┌──────────┐    ┌──────────┐
   │Agent Move│    │Track It! │ ◄── FR3.3
   └──────────┘    └──────────┘
          │               │
          │               ▼
          │    ┌──────────────────┐
          │    │ Save to DB:      │
          │    │ - move_number    │
          │    │ - agent_id       │
          │    │ - action         │
          │    │ - board_state    │
          │    └──────────────────┘
          │               │
          └───────┬───────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Game Over?     │
         └─────────────────┘
           No │        │ Yes
              │        │
              └────┐   │
                   │   │
                   ▼   ▼
              ┌─────────────────┐
              │ Determine Winner│
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Update Contest  │
              │ - winner_id     │
              │ - status=done   │
              └─────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Update Records   │ ◄── FR3.4
              │ - Winner: +1 win │
              │ - Loser: +1 loss │
              │ (or both +1 draw)│
              └──────────────────┘


3. VIEW RESULTS
   ┌──────────────────────────────┐
   │ User clicks "View" button    │
   └──────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ GET /api/contests/:id                  │
   └────────────────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ Fetch Contest + All Actions            │
   │ JOIN contest_actions ON contest_id     │
   └────────────────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ Display in ContestDetailsView          │
   │ - Contest info                         │
   │ - Winner                               │
   │ - Move-by-move history                 │
   │ - Expandable board states              │
   └────────────────────────────────────────┘


4. VIEW AGENT RECORDS (FR3.4)
   ┌──────────────────────────────┐
   │ Display AgentRecordsList     │
   └──────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ For each agent:                        │
   │ GET /api/agents/:id/record             │
   └────────────────────────────────────────┘
                  │
                  ▼
   ┌────────────────────────────────────────┐
   │ Display Table:                         │
   │ Agent | Wins | Losses | Draws | Total  │
   │   A   |  5   |   2    |   1   |   8    │
   │   B   |  3   |   4    |   0   |   7    │
   └────────────────────────────────────────┘
```

## Component Hierarchy

```
/contests (Page)
├── ContestCreationForm
│   ├── Input (name)
│   ├── Select (game)
│   ├── Checkbox (auto-match)
│   ├── Select (agent1) - conditional
│   ├── Select (agent2) - conditional
│   └── Button (submit)
│
├── ContestList
│   ├── Select (status filter)
│   └── Table
│       └── For each contest:
│           ├── Contest info
│           ├── Button (Run) - if pending
│           └── Button (View)
│
├── Modal (Create Contest)
│   └── ContestCreationForm
│
└── Modal (View Details)
    └── ContestDetailsView
        ├── Contest Info Card
        │   ├── Name, Game, Status
        │   ├── Agent 1 Info
        │   ├── Agent 2 Info
        │   └── Winner (if completed)
        │
        └── Action History
            └── For each action:
                ├── Move number
                ├── Agent name
                ├── Action taken
                └── Details (expandable)
                    └── Board state
```

## Data Flow Diagram

```
┌───────────┐
│  User     │
└─────┬─────┘
      │ 1. Create Contest
      ▼
┌─────────────────┐
│ Frontend Form   │
└────────┬────────┘
         │ 2. POST /api/contests
         │    {name, game, agents...}
         ▼
┌─────────────────┐
│  Backend API    │
└────────┬────────┘
         │ 3. INSERT INTO contests
         ▼
┌─────────────────┐
│   Database      │
└────────┬────────┘
         │ 4. Return contest_id
         ▼
┌─────────────────┐
│  Frontend       │
│  (Contest List) │
└────────┬────────┘
         │ 5. User clicks "Run"
         ▼
┌─────────────────┐
│  Backend API    │
│  /run endpoint  │
└────────┬────────┘
         │ 6. Load agents from filesystem
         │    games/conn4/agents/students/...
         ▼
┌─────────────────┐
│  Game Engine    │
│  Execute Loop   │
└────────┬────────┘
         │ 7. For each move:
         │    INSERT INTO contest_actions
         │    (move#, agent, action, board)
         ▼
┌─────────────────┐
│   Database      │
│  (Actions)      │
└────────┬────────┘
         │ 8. Game complete
         │    UPDATE contests (winner)
         │    UPDATE agent_records
         ▼
┌─────────────────┐
│   Database      │
│  (Contest done) │
└────────┬────────┘
         │ 9. Return result
         ▼
┌─────────────────┐
│  Frontend       │
│  Show winner    │
└─────────────────┘
```

## File Structure

```
CompetitiveAgentsSite/
│
├── PythonWebserver/
│   ├── app.py                     ◄── Contest endpoints added
│   ├── dbSetup.py                 ◄── New tables added
│   └── games/
│       ├── conn4/
│       │   ├── game.py            ◄── Used by contest execution
│       │   └── agents/students/   ◄── Agent files loaded here
│       └── tictactoe/
│           ├── game.py
│           └── agents/students/
│
└── competitive-agent-site/
    └── src/
        ├── app/
        │   └── contests/
        │       └── page.tsx       ◄── Main contest page
        │
        └── components/
            ├── contests/          ◄── NEW FOLDER
            │   ├── ContestCreationForm.tsx
            │   ├── ContestList.tsx
            │   └── ContestDetailsView.tsx
            │
            ├── agents/
            │   └── AgentRecordsList.tsx  ◄── NEW
            │
            └── ui/
                ├── Button.tsx     ◄── Used by contest components
                ├── Input.tsx      ◄── Used by contest components
                ├── Modal.tsx      ◄── Used by contest page
                └── Table.tsx      ◄── Used by contest list
```

## Database Relationships

```
┌──────────┐
│  groups  │
└────┬─────┘
     │ 1
     │
     │ N
┌────┴─────┐         ┌──────────────┐
│  agents  │◄────────┤agent_records │
└────┬─────┘ 1    1  └──────────────┘
     │               (wins/losses/draws)
     │ N
     │
     │ 2 (agent1, agent2)
┌────┴──────┐
│ contests  │
└────┬──────┘
     │ 1
     │
     │ N
┌────┴────────────┐
│contest_actions  │
└─────────────────┘
(move-by-move tracking)
```

## Key Features Map

```
FR3.1: Initiate Contests
├── Manual Selection
│   └── ContestCreationForm (agent dropdowns)
└── Backend: POST /api/contests

FR3.2: Auto-Match
├── Checkbox in Form
└── Backend: Random agent selection

FR3.3: Action Tracking
├── During Execution
│   ├── Modified game loop
│   └── Save to contest_actions table
└── View Results
    └── ContestDetailsView component

FR3.4: Win/Loss Records
├── After Contest Complete
│   └── Update agent_records table
└── View Records
    └── AgentRecordsList component
```

---

This architecture supports scalability and can be extended for:

- Tournament Management (FR4.x)
- Leaderboards (FR5.x)
- Real-time updates via WebSockets
- Contest scheduling
- Batch execution of contests
