# Moving the YNAB Reporter into Claude Cowork

Cowork runs this project locally with the same agentic engine as Claude Code,
can use your Gmail connector, and can run the report on a schedule. The code
barely changes — most of the work is relocating the folder and wiring up
secrets and permissions.

## Prerequisites

- A paid Claude plan (Pro, Max, Team, or Enterprise).
- The Claude desktop app on macOS or Windows, updated to the latest version.
- In the app, switch to the **Cowork** tab ("Tasks").

## One-time setup

1. **Put this folder on your computer.** Cowork works on real local folders it
   can read and write. Place `ynab-reporter/` somewhere convenient, and when you
   start a Cowork task, grant access to that folder.

2. **Add your token to `.env`.** Copy `.env.example` to `.env` and paste your
   YNAB token and budget ID. `.env` is gitignored, and Cowork runs in a local
   sandbox VM, so the token stays on your machine.

3. **Allowlist `api.ynab.com`.** Cowork respects your network egress
   permissions, so add `api.ynab.com` to your allowed domains. This applies to
   the script's direct API call; it does not affect the Gmail step, which runs
   through a connector.

4. **Set folder instructions.** Paste the contents of `CLAUDE.md` into Cowork's
   folder-instructions field for this folder (Settings -> Cowork, or when you
   select the folder). That tells Cowork how to run the two report modes without
   re-explaining each time. Keeping `CLAUDE.md` in the folder also serves as a
   checked-in reference.

5. **Confirm the Gmail connector is on.** The email step uses the same Gmail
   connector you already have; make sure it's enabled for Cowork.

## Running it

Start a Cowork task on the folder and say, e.g., "run the month-to-date report
and draft the email." Cowork installs dependencies on first run, fetches from
YNAB, builds the report, and creates a Gmail draft for you to review.

Do a first run while watching to confirm the transactions and draft look right.

## Scheduling (optional)

To automate it, type `/schedule` in a Cowork task — for example, a full report
on the 1st of each month.

**Caveat:** Cowork's scheduler is not a server cron. Scheduled tasks run only
while your computer is awake and the desktop app is open; if it's closed at the
scheduled time, the task runs the next time you open the app. If you need
guaranteed unattended delivery, a server cron or GitHub Action is more reliable —
Cowork is best for on-demand and supervised runs.
