from pathlib import Path
p = Path('/d/Portable_Soft/hermes/skills/autonomous-ai-agents/always-on-agent/scripts/medium_sensor_run.py').resolve()
print(p)
print(p.parents[4])
print((p.parents[4] / "scripts" / "finance_core.py").exists())