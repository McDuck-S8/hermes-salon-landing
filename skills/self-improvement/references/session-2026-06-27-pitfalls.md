# Pitfalls from Session 2026-06-27

## "Read Before Building"
NEVER build new features without reading existing code first. User corrected: "ты читал его файлы... неужели не увидел". Always check _deprecated/, existing scripts, and related modules before creating new ones. The pattern may already exist.

## "Update DOX Immediately"
After creating new files/scripts, IMMEDIATELY update AGENTS.md and scripts/AGENTS.md. User corrected: "ты занес изменения в DOX файлах?" Forgetting documentation = system becomes undocumented and unmaintainable.

## "Questions on Reflexes"
Procedural triggers must ask WHY, not just WHAT. User corrected: "правильные вопросы нужно задавать на рефлексах!!!!" When a trigger fires: (1) What happened? (2) Why? (3) How often? (4) What does it mean for the system? This is how reflexes become learning.

## "Save Learnings Immediately"
When user asks "ты сцуко куда то это записал????" — learnings MUST be saved to memory/skills RIGHT NOW, not "later". Delayed saving = lost learning. Record to memory AND create/update skill in the same turn.

## "Action Over Analysis"
User said "чего ждем?" three times while I was analyzing instead of acting. Analysis without action = failure. After understanding the problem, IMMEDIATELY take the next concrete step. Stop when you need user input, not before.

## "Know System Configuration"
V2RayN proxy: HTTP on port 10809, SOCKS5 on 10806 (unreliable). Must know proxy ports, API endpoints, and system config before debugging. User corrected: "V2RayN работает и я смотрю ютуб" — I assumed proxy was down when it was actually working.

## "Verify Files Exist Before Telling User to Run"
User got error "auto-fix-russia-preset.bat не является внутренней или внешней командой" because I told them to run a file that doesn't exist. ALWAYS verify file exists before suggesting user run it.
