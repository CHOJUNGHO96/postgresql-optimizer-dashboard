# AI Optimization Schema Fix - Implementation Summary

## Problem Identified

**Root Cause**: Schema mismatch between configuration default and actual usage

1. **`.env.example`** (line 7): `DB_SCHEMA=pgs_analysis` ✅
2. **`config.py`** (line 27): `DB_SCHEMA: str = "public"` ❌ **MISMATCH!**
3. **`models.py`** (line 33): `{"schema": "pgs_analysis"}` ✅ Hardcoded
4. **Migration** (line 26): `TARGET_SCHEMA = get_settings().DB_SCHEMA` ✅

**Impact**:
- If `.env` file doesn't set `DB_SCHEMA`, the default `"public"` is used
- Data gets saved to `public.optimized_queries`
- But queries search in `pgs_analysis.optimized_queries`
- Result: POST succeeds but GET returns empty array

## Changes Implemented

### 1. Fixed Configuration Default (MANDATORY)

**File**: `backend/app/core/config.py` (line 27)

```python
# BEFORE:
DB_SCHEMA: str = "public"

# AFTER:
DB_SCHEMA: str = "pgs_analysis"
```

**Reason**: Align default value with project standard and .env.example

### 2. Fixed Deprecated datetime Usage (RECOMMENDED)

**File**: `backend/app/infrastructure/ai_optimization/models.py`

```python
# Import change (line 4):
from datetime import datetime, timezone

# Default value change (line 90):
# BEFORE:
default=datetime.utcnow,

# AFTER:
default=lambda: datetime.now(timezone.utc),
```

**Reason**: `datetime.utcnow()` is deprecated in Python 3.12+

### 3. Re-ran Migration

```bash
cd backend
alembic downgrade -1  # Remove optimized_queries table
alembic upgrade head   # Recreate with correct schema (pgs_analysis)
```

## Verification Steps

### Step 1: Database Schema Verification

Run the SQL verification script:

```bash
cd backend
psql -U postgres -d optimizer_dashboard -f verify_schema.sql
```

**Expected Results**:
- ✅ `pgs_analysis` schema exists
- ✅ `optimized_queries` table in `pgs_analysis` schema
- ✅ FK constraint points to `pgs_analysis.query_plans`
- ✅ 4 indexes created (original_plan_id, ai_model, created_at, confidence_score)

### Step 2: Backend Server Test

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Start server**:
```bash
uvicorn app.main:app --reload --port 8000
```

3. **Test API** (requires existing query_plan record):

```bash
# Create query analysis first (with valid SQL)
curl -X POST "http://localhost:8000/api/v1/query-analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT 1",
    "title": "Test Query"
  }'

# Get plan_id from response, then optimize
curl -X POST "http://localhost:8000/api/v1/query-analysis/{plan_id}/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_model": "claude-3-5-sonnet-20241022",
    "validate_optimization": false
  }'

# Get optimization history
curl -X GET "http://localhost:8000/api/v1/query-analysis/{plan_id}/optimize"
```

### Step 3: Frontend Integration Test

1. **Start frontend**:
```bash
cd frontend
npm run dev
```

2. **Manual test**:
   - Navigate to query analysis page
   - Click "AI 최적화" button
   - Select AI model
   - Run optimization
   - **Expected**: Results appear immediately in "AI 최적화 이력" section

## Success Criteria

### Database Level ✅
- [x] `pgs_analysis` schema exists
- [x] `pgs_analysis.optimized_queries` table exists
- [x] `pgs_analysis.query_plans` table exists
- [x] FK constraint valid: `optimized_queries.original_plan_id → query_plans.id`
- [x] 4 indexes created

### Configuration Level ✅
- [x] `config.py` default matches `.env.example`
- [x] No hardcoded schema mismatches
- [x] Migration uses `get_settings().DB_SCHEMA`

### Code Level ✅
- [x] Deprecated `datetime.utcnow` replaced
- [x] Timezone-aware datetime usage
- [x] Type hints correct

### API Level (Pending Functional Test)
- [ ] POST `/api/v1/query-analysis/{plan_id}/optimize` → 201 Created
- [ ] GET `/api/v1/query-analysis/{plan_id}/optimize` → 200 OK, non-empty array
- [ ] Data persists in correct schema
- [ ] FK integrity maintained

### Frontend Level (Pending Functional Test)
- [ ] Optimization results display immediately
- [ ] No console errors
- [ ] Network requests succeed (201, 200)
- [ ] React Query cache updated

## Files Modified

1. **`backend/app/core/config.py`** - Fixed DB_SCHEMA default
2. **`backend/app/infrastructure/ai_optimization/models.py`** - Fixed deprecated datetime
3. **Database** - Re-ran migration 003 with correct schema

## Rollback Plan

If issues occur:

```bash
# Revert code changes
git checkout backend/app/core/config.py
git checkout backend/app/infrastructure/ai_optimization/models.py

# Revert database
cd backend
alembic downgrade -1

# Restore to public schema (if needed)
# Run SQL to move tables back to public schema
```

## Next Steps

1. **Manual Testing**: Complete functional tests with real data
2. **Validation**: Verify all success criteria
3. **Monitoring**: Check logs for errors
4. **Cleanup**: Remove temporary verification files
5. **Documentation**: Update project documentation

## Notes

- The fix is backward compatible (existing .env files with DB_SCHEMA=pgs_analysis work)
- The fix ensures consistency even without .env file
- No data migration needed (tables were empty)
- Frontend code unchanged (no updates needed)
