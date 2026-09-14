-- ============================================================
-- PS DIGITAL — Database Migration
-- Run this ONCE in Supabase: Dashboard → SQL Editor → New Query → paste → Run
-- Safe to re-run: every statement uses IF NOT EXISTS.
-- ============================================================

-- 1. Late / early tracking + branding + shift policy on companies
ALTER TABLE companies ADD COLUMN IF NOT EXISTS brand_color text;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS shift_start_time text;      -- e.g. '09:00'
ALTER TABLE companies ADD COLUMN IF NOT EXISTS late_grace_minutes integer DEFAULT 15;

-- 2. Store the exact time attendance was marked (used for late-tracking + receipts)
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS marked_time text;         -- e.g. '09:12:45'

-- 3. Multiple admins per company
CREATE TABLE IF NOT EXISTS company_admins (
    id bigint generated always as identity primary key,
    company_name text NOT NULL,
    email text NOT NULL,
    added_at timestamptz DEFAULT now(),
    UNIQUE (company_name, email)
);

-- 4. Leave / time-off requests
CREATE TABLE IF NOT EXISTS leave_requests (
    id bigint generated always as identity primary key,
    company_name text NOT NULL,
    employee_email text NOT NULL,
    employee_name text,
    start_date date NOT NULL,
    end_date date NOT NULL,
    reason text,
    status text NOT NULL DEFAULT 'Pending',   -- Pending | Approved | Rejected
    requested_at timestamptz DEFAULT now()
);

-- ============================================================
-- ROW LEVEL SECURITY (recommended — see DEPLOYMENT_NOTES.md)
-- ============================================================
-- The app currently authenticates users itself (via email OTP) rather than
-- through Supabase Auth, and uses the shared "anon" key for every request.
-- That means if RLS is OFF, anyone holding your anon key (visible in the
-- deployed app's requirements/network calls) could query ANY row in these
-- tables directly through the Supabase REST API, bypassing the app's own
-- access checks entirely.
--
-- Because this app doesn't use Supabase Auth sessions, "per-user" RLS
-- policies aren't straightforward to write safely from inside the database
-- alone. The practical fix that matches how this app works today is:
--   1. Rotate your anon key regularly.
--   2. Keep the anon key out of your public GitHub repo (use Streamlit
--      secrets — see DEPLOYMENT_NOTES.md).
--   3. If you want database-level enforcement, the most robust path is to
--      migrate this app to real Supabase Auth (magic-link or OTP via
--      Supabase itself) so you can write RLS policies keyed off auth.uid().
--      That's a bigger change than this migration and is not included here
--      — ask if you'd like help planning that migration separately.
