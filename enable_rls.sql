-- ============================================================
-- PS DIGITAL — Enable RLS Safely
-- Run this in Supabase: Dashboard → SQL Editor → New Query → paste → Run
--
-- IMPORTANT CONTEXT:
-- This app authenticates users itself (email OTP) rather than through
-- Supabase Auth, and every request from the app uses the same shared
-- "anon" key regardless of which person is using it. That means:
--
--   - Real per-row restriction ("employee X can only see employee X's
--     data") is NOT achievable at the database level with this
--     architecture, because Supabase has no way to tell which app-user
--     is making the request — they all look identical (same anon key).
--   - The app itself already enforces "who can see what" in its own code
--     (filtering by company_name / email before showing data on screen).
--   - What RLS *can* still do here: stop anyone who is NOT using your app
--     (e.g. someone who found your anon key) from directly querying the
--     Supabase REST API with a different role, and stop RLS being "off"
--     from showing up as a red flag in security audits/scanners.
--
-- This script turns RLS ON and explicitly allows the "anon" role to do
-- exactly what the app already does — no more, no less. This is why
-- turning RLS on previously broke everything: it was enabled with ZERO
-- policies, which blocks all access by default. These policies fix that.
-- ============================================================

-- companies
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON companies;
CREATE POLICY "anon_full_access" ON companies
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- employees
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON employees;
CREATE POLICY "anon_full_access" ON employees
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- attendance
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON attendance;
CREATE POLICY "anon_full_access" ON attendance
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- company_notices
ALTER TABLE company_notices ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON company_notices;
CREATE POLICY "anon_full_access" ON company_notices
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- company_admins (only if you ran migration.sql already)
ALTER TABLE company_admins ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON company_admins;
CREATE POLICY "anon_full_access" ON company_admins
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- leave_requests (only if you ran migration.sql already)
ALTER TABLE leave_requests ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "anon_full_access" ON leave_requests;
CREATE POLICY "anon_full_access" ON leave_requests
    FOR ALL TO anon USING (true) WITH CHECK (true);

-- ============================================================
-- After running this:
--   - RLS shows as "Enabled" in the Supabase dashboard (no more warning).
--   - Your app keeps working exactly as before — nothing changes for users.
--   - Anyone querying with a role OTHER than anon/service_role (there
--     usually isn't one, so this is mostly a safety net) is blocked.
--
-- What this does NOT do:
--   - It does not stop someone who has your anon key from reading/writing
--     any row in these tables directly via the API. That protection
--     requires either rotating the key immediately if it's ever exposed
--     (see DEPLOYMENT_NOTES.md) or migrating to real Supabase Auth so
--     policies can check auth.uid() instead of just "is this anon".
-- ============================================================
