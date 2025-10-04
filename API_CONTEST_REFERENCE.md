# Contest Management API Reference

## Base URL

```
http://localhost:5000
```

## Authentication

All endpoints require authentication via session cookies.  
Include `credentials: "include"` in fetch requests.

---

## Endpoints

### 1. Create Contest

**FR3.1: Manual Contest Creation**  
**FR3.2: Auto-Match Contest**

```http
POST /api/contests
Content-Type: application/json
```

#### Request Body (Manual)

```json
{
  "name": "Championship Match",
  "game": "conn4",
  "agent1_id": 1,
  "agent2_id": 2
}
```

#### Request Body (Auto-Match)

```json
{
  "name": "Random Match",
  "game": "tictactoe",
  "auto_match": true
}
```

#### Response (201 Created)

```json
{
  "message": "Contest created successfully",
  "contest_id": 1
}
```

#### Error Responses

- **400 Bad Request**: Missing required fields or invalid agent IDs
- **401 Unauthorized**: User not logged in
- **500 Internal Server Error**: Database or server error

---

### 2. Run Contest

**FR3.3: Execute Contest and Track Actions**  
**FR3.4: Update Win/Loss Records**

```http
POST /api/contests/{contest_id}/run
```

#### Response (200 OK)

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
    },
    {
      "move_number": 1,
      "agent_id": 2,
      "action": "2",
      "board_state": "['', '', 'O', 'X', '', '', '']"
    }
  ]
}
```

#### Notes

- `winner_id` is `null` for draws
- Actions array contains complete move-by-move history
- Automatically updates `agent_records` table

#### Error Responses

- **400 Bad Request**: Contest already completed or invalid game
- **404 Not Found**: Contest doesn't exist
- **500 Internal Server Error**: Game execution error

---

### 3. Get All Contests

```http
GET /api/contests?status={filter}
```

#### Query Parameters

- `status` (optional): Filter by status
  - `all` (default): All contests
  - `pending`: Only pending contests
  - `completed`: Only completed contests

#### Response (200 OK)

```json
{
  "contests": [
    {
      "contest_id": 1,
      "name": "Championship Match",
      "game": "conn4",
      "agent1_id": 1,
      "agent1_name": "MiniMaxAgent",
      "agent2_id": 2,
      "agent2_name": "RandomAgent",
      "winner_id": 1,
      "status": "completed",
      "created_at": "2025-10-04T10:30:00",
      "completed_at": "2025-10-04T10:31:00"
    }
  ]
}
```

---

### 4. Get Contest Details

**FR3.3: View Complete Action History**

```http
GET /api/contests/{contest_id}
```

#### Response (200 OK)

```json
{
  "contest": {
    "contest_id": 1,
    "name": "Championship Match",
    "game": "conn4",
    "agent1": {
      "id": 1,
      "name": "MiniMaxAgent",
      "group": "group1"
    },
    "agent2": {
      "id": 2,
      "name": "RandomAgent",
      "group": "group2"
    },
    "winner_id": 1,
    "status": "completed",
    "created_at": "2025-10-04T10:30:00",
    "completed_at": "2025-10-04T10:31:00"
  },
  "actions": [
    {
      "move_number": 0,
      "agent_id": 1,
      "agent_name": "MiniMaxAgent",
      "action": "3",
      "board_state": "['', '', '', 'X', '', '', '']"
    }
  ]
}
```

#### Error Responses

- **404 Not Found**: Contest doesn't exist

---

### 5. Get Agent Record

**FR3.4: View Win/Loss Statistics**

```http
GET /api/agents/{agent_id}/record
```

#### Response (200 OK)

```json
{
  "agent_id": 1,
  "agent_name": "MiniMaxAgent",
  "wins": 5,
  "losses": 2,
  "draws": 1,
  "total_contests": 8
}
```

#### Notes

- `total_contests` = wins + losses + draws
- If agent has never competed, all counts will be 0
- Record automatically created on first contest completion

#### Error Responses

- **404 Not Found**: Agent doesn't exist

---

## Data Models

### Contest

```typescript
{
  contest_id: number;
  name: string;
  game: "conn4" | "tictactoe";
  agent1_id: number;
  agent2_id: number;
  winner_id: number | null; // null for draws
  status: "pending" | "completed";
  created_by: number;
  created_at: string; // ISO 8601 format
  completed_at: string | null;
}
```

### Contest Action

```typescript
{
  action_id: number;
  contest_id: number;
  move_number: number;
  agent_id: number;
  action_data: string; // The move/action taken
  board_state: string; // Board state after action
  created_at: string;
}
```

### Agent Record

```typescript
{
  record_id: number;
  agent_id: number;
  wins: number;
  losses: number;
  draws: number;
}
```

---

## Example Usage (JavaScript/TypeScript)

### Create Contest

```typescript
const response = await fetch("http://localhost:5000/api/contests", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include",
  body: JSON.stringify({
    name: "Test Match",
    game: "conn4",
    agent1_id: 1,
    agent2_id: 2,
  }),
});

const data = await response.json();
console.log(data.contest_id);
```

### Run Contest

```typescript
const response = await fetch(
  `http://localhost:5000/api/contests/${contestId}/run`,
  {
    method: "POST",
    credentials: "include",
  }
);

const result = await response.json();
console.log("Winner:", result.winner_id);
console.log("Total moves:", result.actions.length);
```

### Get Contest Details

```typescript
const response = await fetch(
  `http://localhost:5000/api/contests/${contestId}`,
  { credentials: "include" }
);

const { contest, actions } = await response.json();
console.log(`${contest.name}: ${actions.length} moves`);
```

### Get Agent Record

```typescript
const response = await fetch(
  `http://localhost:5000/api/agents/${agentId}/record`,
  { credentials: "include" }
);

const record = await response.json();
const winRate = ((record.wins / record.total_contests) * 100).toFixed(1);
console.log(`Win rate: ${winRate}%`);
```

---

## Status Codes Summary

| Code | Meaning      | Usage                                      |
| ---- | ------------ | ------------------------------------------ |
| 200  | OK           | Successful GET or POST (run contest)       |
| 201  | Created      | Contest successfully created               |
| 400  | Bad Request  | Invalid input or contest already completed |
| 401  | Unauthorized | User not authenticated                     |
| 404  | Not Found    | Contest or agent doesn't exist             |
| 500  | Server Error | Database or game execution error           |

---

## Testing with cURL

### Create Contest

```bash
curl -X POST http://localhost:5000/api/contests \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "name": "Test Contest",
    "game": "conn4",
    "agent1_id": 1,
    "agent2_id": 2
  }'
```

### Run Contest

```bash
curl -X POST http://localhost:5000/api/contests/1/run \
  -b cookies.txt
```

### Get All Contests

```bash
curl http://localhost:5000/api/contests?status=all \
  -b cookies.txt
```

---

## Related Documentation

- Full Implementation: `CONTEST_IMPLEMENTATION.md`
- Testing Guide: `TESTING_CONTESTS.md`
- Quick Start: `QUICK_START_CONTESTS.md`
