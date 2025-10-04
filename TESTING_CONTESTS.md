# Contest Management Testing Guide (FR3.1-FR3.4)

## Overview

This guide covers testing all Contest Management features implemented for FR3.1 through FR3.4.

## Prerequisites

1. Database should be initialized with groups and agents
2. Backend server running on port 5000
3. Frontend server running on port 3000
4. Logged in as admin user

## Database Setup

### Step 1: Initialize Database

```bash
docker compose up --build
docker compose exec app python dbSetup.py
```

### Step 2: Verify Tables Created

The following new tables should exist:

- `contests` - Stores contest information
- `contest_actions` - Tracks all moves during contests (FR3.3)
- `agent_records` - Tracks win/loss/draw records (FR3.4)

### Step 3: Add Test Groups (if not exists)

```sql
-- Connect to database and run:
INSERT INTO groups (groupname) VALUES ('group1'), ('group2')
ON CONFLICT (groupname) DO NOTHING;
```

## Backend Testing

### Test 1: Create Contest (FR3.1)

**Endpoint:** `POST /api/contests`

**Request:**

```json
{
  "name": "Test Contest 1",
  "game": "conn4",
  "agent1_id": 1,
  "agent2_id": 2
}
```

**Expected Response (201):**

```json
{
  "message": "Contest created successfully",
  "contest_id": 1
}
```

### Test 2: Auto-Match Contest (FR3.2)

**Endpoint:** `POST /api/contests`

**Request:**

```json
{
  "name": "Auto-Match Contest",
  "game": "conn4",
  "auto_match": true
}
```

**Expected Response (201):**

```json
{
  "message": "Contest created successfully",
  "contest_id": 2
}
```

### Test 3: Run Contest with Action Tracking (FR3.3)

**Endpoint:** `POST /api/contests/{contest_id}/run`

**Expected Response (200):**

```json
{
  "message": "Contest completed",
  "winner_id": 1,
  "actions": [
    {
      "move_number": 0,
      "agent_id": 1,
      "action": "3",
      "board_state": "['', '', '', 'X', '', '', '']"
    }
    // ... more actions
  ]
}
```

### Test 4: Get All Contests

**Endpoint:** `GET /api/contests?status=all`

**Expected Response (200):**

```json
{
  "contests": [
    {
      "contest_id": 1,
      "name": "Test Contest 1",
      "game": "conn4",
      "agent1_id": 1,
      "agent1_name": "Agent1",
      "agent2_id": 2,
      "agent2_name": "Agent2",
      "winner_id": 1,
      "status": "completed",
      "created_at": "2025-10-04T...",
      "completed_at": "2025-10-04T..."
    }
  ]
}
```

### Test 5: Get Contest Details

**Endpoint:** `GET /api/contests/{contest_id}`

**Expected Response (200):**

```json
{
  "contest": {
    "contest_id": 1,
    "name": "Test Contest 1",
    "game": "conn4",
    "agent1": { "id": 1, "name": "Agent1", "group": "group1" },
    "agent2": { "id": 2, "name": "Agent2", "group": "group2" },
    "winner_id": 1,
    "status": "completed",
    "created_at": "2025-10-04T...",
    "completed_at": "2025-10-04T..."
  },
  "actions": [
    {
      "move_number": 0,
      "agent_id": 1,
      "agent_name": "Agent1",
      "action": "3",
      "board_state": "['', '', '', 'X', '', '', '']"
    }
  ]
}
```

### Test 6: Get Agent Record (FR3.4)

**Endpoint:** `GET /api/agents/{agent_id}/record`

**Expected Response (200):**

```json
{
  "agent_id": 1,
  "agent_name": "Agent1",
  "wins": 2,
  "losses": 1,
  "draws": 0,
  "total_contests": 3
}
```

## Frontend Testing

### Page 1: Contest Management Page (`/contests`)

#### Test Steps:

1. **Navigate to `/contests`**

   - Should see "Contest Management" heading
   - Should see "Create Contest" button
   - Should see contest list table

2. **Create Contest (FR3.1)**

   - Click "Create Contest" button
   - Modal should open
   - Fill in:
     - Contest Name: "My First Contest"
     - Game: Select "Connect 4"
     - Agent 1: Select from dropdown
     - Agent 2: Select different agent from dropdown
   - Click "Create Contest"
   - Modal should close
   - New contest should appear in list with "pending" status

3. **Create Auto-Match Contest (FR3.2)**

   - Click "Create Contest" button
   - Check "Auto-match agents" checkbox
   - Agent dropdowns should disappear
   - Fill in Contest Name and Game
   - Click "Create Contest"
   - New contest should appear with automatically selected agents

4. **Run Contest (FR3.3)**

   - Find pending contest in list
   - Click "Run" button
   - Button should show "Running..." state
   - After completion:
     - Status should change to "completed"
     - "Run" button should disappear

5. **View Contest Details (FR3.3)**

   - Click "View" button on any completed contest
   - Modal should open showing:
     - Contest name, game, status
     - Both agents with group names
     - Winner information
     - Move-by-move history with board states
   - Each action should show:
     - Move number
     - Agent name
     - Action taken
     - Expandable board state

6. **Filter Contests**
   - Change filter dropdown to "Pending"
   - Should only show pending contests
   - Change to "Completed"
   - Should only show completed contests

### Page 2: Agent Records Display

You can add the `AgentRecordsList` component to the admin dashboard or contests page:

```tsx
import AgentRecordsList from "@/components/agents/AgentRecordsList";

// Add to page:
<div className="bg-white rounded-lg shadow p-6 mt-6">
  <AgentRecordsList />
</div>;
```

#### Test Steps:

1. **View Agent Records (FR3.4)**
   - Should see table with all agents
   - Columns: Agent Name, Wins, Losses, Draws, Total Contests, Win Rate
   - Win rate should be calculated correctly (wins / total \* 100)
   - Agents with no contests should show 0% win rate

## Error Cases to Test

### Backend Errors:

1. **Missing Required Fields**

   - POST `/api/contests` with empty name
   - Expected: 400 error

2. **Invalid Agent IDs**

   - POST `/api/contests` with non-existent agent IDs
   - Expected: 400 error "One or both agents not found"

3. **Contest Not Found**

   - GET `/api/contests/99999`
   - Expected: 404 error

4. **Run Already Completed Contest**

   - POST `/api/contests/{completed_contest_id}/run`
   - Expected: 400 error "Contest already completed"

5. **Auto-match with Insufficient Agents**
   - POST `/api/contests` with auto_match=true when < 2 agents exist for game
   - Expected: 400 error "Not enough agents for auto-matching"

### Frontend Errors:

1. **Unauthorized Access**

   - Try accessing /contests without login
   - Should redirect to login page

2. **Network Errors**
   - Stop backend server
   - Try creating contest
   - Should show appropriate error message

## Verification Checklist

- [ ] FR3.1: Can create contests manually by selecting agents ✓
- [ ] FR3.2: Can create contests with automatic agent matching ✓
- [ ] FR3.3: Contest runs track every action/move with board state ✓
- [ ] FR3.3: Can view complete move history after contest completion ✓
- [ ] FR3.4: Agent win/loss/draw records are updated after contests ✓
- [ ] FR3.4: Can view agent records with win rate calculation ✓
- [ ] Contest list shows all contests with status filtering
- [ ] Contest details modal displays complete information
- [ ] Real-time updates when new contests are created
- [ ] Database properly stores contests, actions, and records
- [ ] Error handling works for all edge cases

## Database Queries for Verification

### Check Contests Created:

```sql
SELECT * FROM contests ORDER BY created_at DESC;
```

### Check Contest Actions:

```sql
SELECT ca.*, a.name
FROM contest_actions ca
JOIN agents a ON ca.agent_id = a.agent_id
WHERE contest_id = 1
ORDER BY move_number;
```

### Check Agent Records:

```sql
SELECT ar.*, a.name
FROM agent_records ar
JOIN agents a ON ar.agent_id = a.agent_id;
```

## Next Steps After Testing

Once all tests pass:

1. Document any bugs found and fixes applied
2. Take screenshots of working features
3. Prepare for Tournament Management (FR4.x) implementation
4. Consider performance optimization for large numbers of contests
