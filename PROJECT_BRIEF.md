# Unisco — Project Brief

## What this is
Personalized scholarship & grant matching web service for university students in Daejeon, Korea. Users input their spec (grade level, major, income bracket, region, etc.) and get matched with scholarships/grants they're actually eligible for — modeled after scholarships.com, but scoped tightly to Daejeon university students instead of trying to cover all of Korea.

## Why this scope
Korea already has government-run matching services (온통청년, 복지로, 한국장학재단) covering the whole country, but their UX is fragmented and clunky. Going broad would mean competing directly with government infra with zero budget. Narrowing to Daejeon university students makes the data manageable, verifiable by hand early on, and gives a clear underserved niche.

## Team & roles
- **호성 (repo owner, hoseongdev)**: PM + full-stack developer. Owns architecture, implementation, technical decisions.
- **Friend (non-technical, no dev experience)**: Data collection & structuring (scholarship/grant eligibility rules), content, possibly user research/marketing. Not writing code.

## MVP scope (v1 target)
1. **Users input a spec**: school year, major, income bracket (소득분위), region, military service status (optional fields TBD)
2. **Matching**: rule-based filtering against a structured database of scholarships/grants — no ML needed for v1, just eligibility-condition matching
3. **Data sources (initial)**: 국가장학금, a handful of Daejeon-area university/local scholarship foundations, relevant youth policy grants — manually curated/structured to start, not full automated scraping yet
4. **Core differentiator**: one-time spec input → clean, personalized list. Better onboarding UX than government portals, nothing more ambitious for v1.

## Explicitly out of scope for now
- Nationwide coverage
- Automated scraping pipelines (start manual/semi-manual)
- Any ML/recommendation scoring beyond rule-based filtering
- Monetization/revenue features — this comes after real users, not before

## Naming
- Repo: `UniSco` (owner: hoseongdev)
- Name is a portmanteau of "University" + "Scholarship" — intentional choice, not up for bikeshedding

## Immediate ask (this session)
Do NOT start building features yet. First, just set up the project skeleton:
- Recommend and set up a tech stack (full-stack, reasonably simple — this is a portfolio + real-use project, not an enterprise system)
- Initialize folder structure, basic tooling (linting, env config, etc.)
- Set up a minimal placeholder frontend + backend that runs locally
- Leave a clear TODO/next-steps section for where feature work picks up

Ask clarifying questions if the stack choice needs my input before proceeding.