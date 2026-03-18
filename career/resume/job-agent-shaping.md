---
shaping: true
---

# Passive Job Agent — Shaping Doc

---

## Frame

### Source
> "Think of it as an agent that sources jobs automatically for you."
> "I would just save it but never act on it."
> "I wished there would be a service that can help me auto apply, with tailored resumes."
> "It's for busy working professionals to apply jobs when they only have time to skim."
> "I would just spend 30 minutes every day going through the pile."
> "I can just save links into a Google Sheet, and that is effectively the database."
> "The yes is really down to me to decide — I can't have a one size fits all process."
> "The system's job is to make the cost of acting on a yes as close to zero as possible."

---

### Problem
Senior professionals find good jobs but never apply. Not because they can't find them — browsing is easy. The bottleneck is the application process itself: tailoring a resume, writing a cover letter, filling out forms. It takes more focused time than a busy person has free. So jobs get saved and forgotten.

The yes/no decision on whether to apply is irreducibly human — it's based on career instincts that can't be templated. The system's role is not to decide, score, or filter. It's to eliminate every ounce of friction that comes *after* the decision is made.

### Outcome
A senior professional can go from "I want this job" to "application submitted" in a single 30-minute daily session — without writing a word, filling a form, or visiting a job board.

---

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | After marking a job yes, the user should be able to submit an application with minimal effort | Core goal |
| R1 | The yes/no decision is always made by the user — the system never filters or scores on their behalf | Must-have |
| R2 | Saving a job should be frictionless — a share from phone, nothing more | Must-have |
| R3 | The full workflow fits within a 30-minute daily desktop session | Must-have |
| R4 | Application materials (resume, cover letter) are tailored per job, not generic | Must-have |
| R5 | The user picks the angle to highlight — the system executes, not decides | Must-have |
| R6 | System handles the actual form submission (Playwright automation) | Must-have |
| R7 | User is present to supervise and unblock the submission if needed | Must-have |
| R8 | Google Sheet is the database — no new tool to learn for saving and reviewing | Leaning yes |
| R9 | Works across job boards — not locked to one source | Must-have |
| R10 | Volume is low and selective — quality over quantity (~1 application/week) | Context |

---

## The Flow (as understood)

```
Phone                     Background              Desktop (30 min)
─────                     ──────────              ────────────────
Browse anywhere      →    Link lands in     →     Open Google Sheet
See something good        Google Sheet            Mark yes / no
Share URL to sheet                                ↓ (for each yes)
                                                  System preps application
                                                  User picks angle/keywords
                                                  Review materials
                                                  Click apply
                                                  Playwright submits
                                                  User supervises
```

---

## Open Questions

| # | Question | Blocks |
|---|----------|--------|
| Q1 | What does "prep" look like when the user opens a yes job? What should already be ready vs. what do they provide in the session? | R4, R5 |
| Q2 | How does Playwright handle boards that require login, CAPTCHAs, or multi-step forms? | R6, R7 |
| Q3 | Does the system need to parse the job description to suggest tailoring options, or does the user just type free-form what to highlight? | R5 |

---

## Shapes (ready to explore)
R is stable enough to start sketching shapes. Next step.
