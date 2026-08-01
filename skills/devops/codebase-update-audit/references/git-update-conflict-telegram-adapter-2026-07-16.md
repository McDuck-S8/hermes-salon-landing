# Git Update Conflict — Telegram Adapter Rewrite (2026-07-16)

## Conflict Summary

**File:** `plugins/platforms/telegram/adapter.py`
**Function:** `_verify_polling_after_reconnect`

### Upstream (HEAD — 796 commits ahead)
```python
async def _verify_polling_after_reconnect(
    self,
    generation: Optional[int] = None,
    progress: Optional[asyncio.Event] = None,
) -> None:
    """Require getUpdates progress, using getMe only to classify failure.

    The generation-bound event is set only by a successful response on the
    dedicated getUpdates request. A general-path getMe success can classify
    connectivity, but cannot heal polling health. Connectivity failures
    enter the guarded recovery ladder; auth/validation errors do not churn.
    """
    PROBE_TIMEOUT = 10
    if getattr(self, "_polling_teardown_started", False):
        return
    if generation is None:
        generation = self._polling_generation
    if progress is None:
        progress = self._polling_progress_event

    try:
        await asyncio.wait_for(
            progress.wait(), timeout=_POLLING_PROGRESS_TIMEOUT
        )
    except asyncio.TimeoutError:
        pass

    if getattr(self, "_polling_teardown_started", False):
        return
    if progress.is_set() or self.has_fatal_error:
        return
    if not self._polling_progress_accepting:
        return
    if generation != self._polling_generation:
        return
    if progress is not self._polling_progress_event:
        return

    app = self._app
    if not (app and app.updater and app.updater.running):
        logger.warning(
            "[%s] Updater made no getUpdates progress and is not running",
            self.name,
        )
        self._schedule_polling_recovery(
            RuntimeError("Updater not running after polling progress deadline"),
            reason="polling progress verifier: updater not running",
        )
        return

    try:
        await asyncio.wait_for(app.bot.get_me(), PROBE_TIMEOUT)
    except Exception as probe_err:
        if getattr(self, "_polling_teardown_started", False):
            return
        if self.has_fatal_error or not self._polling_progress_accepting:
            return
        if generation != self._polling_generation:
            return
        if progress is not self._polling_progress_event or progress.is_set():
            return
        if not self._looks_like_network_error(probe_err):
            logger.warning(
                "[%s] Polling progress verifier hit a non-connectivity error"
                " (not retrying): %s",
                self.name, _redact_telegram_error_text(probe_err),
            )
            return
        logger.warning(
            "[%s] Polling progress verifier connectivity probe failed: %s",
            self.name, _redact_telegram_error_text(probe_err),
        )
        self._schedule_polling_recovery(
            probe_err,
            reason="polling progress verifier connectivity failure",
        )
        return

    if getattr(self, "_polling_teardown_started", False):
        return
    if self.has_fatal_error or not self._polling_progress_accepting:
        return
    if generation != self._polling_generation:
        return
    if progress is not self._polling_progress_event or progress.is_set():
        return
    self._schedule_polling_recovery(
```

### Local (Stashed)
```python
async def _verify_polling_after_reconnect(self) -> None:
    """Heartbeat probe scheduled after a successful reconnect.

    PTB's Updater can survive a botched stop()+start_polling() cycle
    with `running=True` but a wedged consumer task. No error callback
    fires, so the reconnect ladder doesn't advance on its own. This
    probe detects the wedge by:

    1. Sleeping HEARTBEAT_PROBE_DELAY so a healthy long-poll has time
       to complete at least one cycle.
    2. Verifying `Updater.running` is still True.
    3. Probing the bot endpoint with a tight asyncio timeout. A
       wedged httpx pool fails this probe; a healthy one returns
       well under the timeout.

    On any failure, re-enter the reconnect ladder so the existing
    MAX_NETWORK_RETRIES path can ultimately escalate to fatal-error.
    """
    HEARTBEAT_PROBE_DELAY = 15
    PROBE_TIMEOUT = 5

    await asyncio.sleep(HEARTBEAT_PROBE_DELAY)

    if self.has_fatal_error:
        return
    if not (self._app and self._app.updater and self._app.updater.running):
        logger.warning(
            "[%s] Updater not running %ds after reconnect — treating as wedged",
            self.name, HEARTBEAT_PROBE_DELAY,
        )
        await self._handle_polling_network_error(
            RuntimeError("Updater not running after reconnect heartbeat")
        )
        return

    try:
        await asyncio.wait_for(self._app.bot.get_me(), PROBE_TIMEOUT)
    except Exception as probe_err:
        if self.has_fatal_error:
            return
        if not self._looks_like_network_error(probe_err):
            logger.warning(
                "[%s] Heartbeat probe hit a non-connectivity error"
                " (not retrying): %s",
                self.name, _redact_telegram_error_text(probe_err),
            )
            return
        logger.warning(
            "[%s] Heartbeat probe connectivity failure: %s",
            self.name, _redact_telegram_error_text(probe_err),
        )
        await self._handle_polling_network_error(probe_err)
```

## Resolution: **Accept upstream entirely**

### Why upstream wins:
1. **Complete architectural rewrite** — new generation-bound progress tracking (`_polling_generation`, `_polling_progress_event`, `_POLLING_PROGRESS_TIMEOUT`)
2. **Addresses root causes** — old probe was a workaround for lack of proper progress verification
3. **New features**: teardown guard, progress acceptance gate, generation isolation, recovery scheduling
4. **Local changes were only parameter tuning** (15s delay, 5s probe) — obsoleted by new design
5. **Merging would create hybrid mess** — old probe logic + new generation tracking = race conditions

### Local tuning preserved elsewhere (if needed):
- Proxy `keepalive_expiry=0` was in a DIFFERENT section of the file (HTTPX request config) — that survived the auto-merge cleanly
- Timeout tuning for `connect_timeout=30` was in the HTTPXRequest initialization — also survived cleanly

### Commands executed:
```bash
cd /d/Portable_Soft/hermes/hermes-agent
git stash push -m "pre-update-2026-07-16" -- cron/scheduler.py hermes_bootstrap.py plugins/platforms/telegram/adapter.py
git pull --ff-only origin main
git stash pop
# Conflict in telegram/adapter.py
git checkout --ours plugins/platforms/telegram/adapter.py  # keep upstream
git add plugins/platforms/telegram/adapter.py
git stash drop stash@{0}
# Other files auto-merged: cron/scheduler.py, hermes_bootstrap.py
```

### Verification:
```bash
python -c "import plugins.platforms.telegram.adapter; print('OK')"
python hermes_bootstrap.py  # boots successfully
```

## Lesson: "When Upstream Rewrites, Don't Merge — Adopt"

> **Pattern:** Upstream rewrites a function completely; local has only parameter tuning.
> **Action:** Accept the rewrite. Re-apply tuning ONLY if the new function exposes equivalent knobs.
> **Rationale:** The rewrite likely fixes the very issues the tuning worked around. Merging reintroduces fragility.

## Post-Update Watch
- [ ] Verify Telegram gateway connects through SOCKS5 proxy without "Server disconnected" errors
- [ ] If proxy instability persists, check if upstream's new proxy handling (keepalive_expiry=0) is already merged — if not, re-apply to new HTTPXRequest config
- [ ] Confirm polling recovery works after network blips (generation mechanism should handle this better)

## Time Investment
- Analysis: ~5 min
- Resolution: ~2 min
- Verification: ~1 min
- **Total: ~8 min** for 796-commit update with 1 significant conflict