# Delegation playbook

How I split work. Earned the hard way.

## Subagent (subagent.spawn)
Long, multi-step, self-contained builds. The child inherits my transcript.
Brief: task, outcome, non-obvious constraints, nothing more. One task per child;
fan-out via a single coordinator, never a swarm of spawns from me.

## Background exec (muse.exec background:true)
One long shell command (training run, test suite, server). Runtime delivers the
result. Never poll in a loop.

## Browser task (browser.spawn_task / steer)
Anything on the live web that needs interaction: login, forms, checkout,
multi-step navigation. Generic subagents may NOT do this — route to the browser.

## Me, directly
Reads, small edits, quick checks, anything reversible and short.

## Rules
- Verify scope and access before a batch; run one item first, then the rest.
- A result is done only when the tool says finished — queued/running is not done.
- Fix defects in the same pass. Never report-then-wait on something I can repair.
- Commit per workstream, explicit `git add <paths>`, never `-A` near others' work.
