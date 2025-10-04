# Quick Start: Contest Management Feature

## 🚀 Getting Started

### 1. Database Setup

```bash
# From project root
docker compose down
docker compose up --build
docker compose exec app python dbSetup.py
```

### 2. Start Services

```bash
# Terminal 1 - Backend (already running in Docker)
docker compose up

# Terminal 2 - Frontend
cd competitive-agent-site
npm run dev
```

### 3. Access Contest Management

Navigate to: **http://localhost:3000/contests**

---

## 📋 Quick Test Checklist

### Before Testing:

- [ ] Ensure you have at least 2 agents uploaded for the same game
- [ ] Logged in as admin user
- [ ] Both backend (port 5000) and frontend (port 3000) running

### Test Sequence:

1. **Create Manual Contest (FR3.1)**

   - Click "Create Contest"
   - Fill form with agent selection
   - Submit

2. **Create Auto-Match Contest (FR3.2)**

   - Click "Create Contest"
   - Check "Auto-match agents"
   - Submit

3. **Run Contest (FR3.3)**

   - Find pending contest
   - Click "Run" button
   - Wait for completion

4. **View Details (FR3.3)**

   - Click "View" on completed contest
   - Check move-by-move history
   - Expand board states

5. **Check Records (FR3.4)**
   - Add `<AgentRecordsList />` to page or admin dashboard
   - Verify win/loss counts updated

---

## 🔧 Troubleshooting

### Problem: Groups dropdown empty

**Solution:** Run initialization script to add groups:

```bash
docker compose exec app python dbSetup.py
```

### Problem: No agents available

**Solution:** Upload agents via the upload form at `/` (main dashboard)

### Problem: Contest won't run

**Check:**

1. Agent files exist at specified paths
2. Agent classes match game configuration
3. Check backend logs: `docker compose logs app`

### Problem: Frontend shows errors

**Check:**

1. Backend running on port 5000
2. CORS configured for your frontend URL
3. Browser console for specific errors

---

## 📊 Database Inspection

### Check contests:

```bash
docker compose exec db psql -U postgres -d test -c "SELECT * FROM contests;"
```

### Check actions:

```bash
docker compose exec db psql -U postgres -d test -c "SELECT * FROM contest_actions WHERE contest_id = 1 ORDER BY move_number;"
```

### Check records:

```bash
docker compose exec db psql -U postgres -d test -c "SELECT ar.*, a.name FROM agent_records ar JOIN agents a ON ar.agent_id = a.agent_id;"
```

---

## 🎯 Key Features Implemented

✅ **FR3.1** - Manual contest creation  
✅ **FR3.2** - Auto-matching agents  
✅ **FR3.3** - Action tracking throughout match  
✅ **FR3.4** - Win/loss record keeping

---

## 📁 Important Files

**Backend:**

- `PythonWebserver/app.py` - Lines 890-1408 (contest endpoints)
- `PythonWebserver/dbSetup.py` - Database schema

**Frontend:**

- `src/app/contests/page.tsx` - Main page
- `src/components/contests/ContestCreationForm.tsx` - Create form
- `src/components/contests/ContestList.tsx` - List view
- `src/components/contests/ContestDetailsView.tsx` - Details view
- `src/components/agents/AgentRecordsList.tsx` - Records table

**Documentation:**

- `TESTING_CONTESTS.md` - Comprehensive testing guide
- `CONTEST_IMPLEMENTATION.md` - Full implementation details
- `QUICK_START_CONTESTS.md` - This file

---

## 🔄 Ready for Next Feature

After verifying everything works:

- Document any issues found
- Commit changes to git
- Ready to implement **FR4.x: Tournament Management** 🏆
