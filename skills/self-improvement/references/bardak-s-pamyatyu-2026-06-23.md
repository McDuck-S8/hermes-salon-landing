## Pitfalls: "Barak s pamyatyu" (2026-06-23)
Agent doesn't know its own tools/departments. Fix: SELF_IDENTITY.md at boot. Details: `references/bardak-s-pamyatyu-2026-06-23.md`

## Pitfalls: "Reporting Instead of Doing" (2026-06-23)
Status reports without action = failure. Details: `references/reporting-is-failure-2026-06-23.md`

## Pitfalls: "Act, Don't Plan" (2026-06-25)
Plans = zero results. Execute ONE action after every plan. Error = data. Details: `references/act-dont-plan-2026-06-25.md`

## Pitfalls: "Serial Retry" (2026-06-25)
Same approach 5x when it failed 2x = fear of switching. After 2 failures, STOP, switch approach. Details: `references/serial-retry-anti-pattern-2026-06-25.md`

## Pitfalls: "Report Without Saving" (2026-06-25)
Useful discovery reported but not saved to ARBITRAGE_WORKSHOP.md, agent_policies.md, or Knowledge Cube = critical error. Must: find → save → report. See `references/report-without-saving-2026-06-25.md`

## Pitfalls: "Can't Read It" (2026-07-02)
Claiming "can't read PDF/binary" instead of finding a tool to read it = failure. PyMuPDF (fitz), pdfplumber, pdftotext, LibreOffice, browser, online extractors — always a way. Never surrender to format. Find the tool, read it, extract value.

## Pitfalls: "Describing Instead of Doing" (2026-07-02)
Reporting "I'll do X" or "X needs to be done" instead of doing X = failure. Tools exist to execute. Use them. The output is the artifact, not the description of the artifact.

## Pitfalls: "Tool Amnesia" (2026-07-02)
Forgetting available tools (web_search, web_extract, browser, vision, pdf readers, terminal) and defaulting to "I can't" = failure. Inventory tools at session start. Use the right tool for the job, not the first tool that comes to mind.