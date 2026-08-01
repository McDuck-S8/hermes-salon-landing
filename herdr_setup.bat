@echo off
echo Creating Herdr spaces...
herdr-multiagent setup --roles orchestrator,coder,browser,researcher,deployer,cpa-operator
echo.
echo Done! Spaces created.
echo Run 'herdr' in Windows Terminal to see them.
pause
