#!/usr/bin/env python3
"""
Human Behavior Engine — Ghost cursor, typing, scrolling, pauses.
Makes automation indistinguishable from human.
"""

import asyncio
import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Callable
from playwright.async_api import Page


@dataclass
class BehaviorProfile:
    """Consistent behavioral quirks for an identity."""
    # Typing
    typing_speed_wpm: float = 60.0          # words per minute
    typing_variance: float = 0.3            # 0-1, how much speed varies
    typo_rate: float = 0.02                 # probability of typo per char
    typo_correction_delay: Tuple[float, float] = (0.1, 0.5)  # seconds before fixing
    
    # Mouse
    mouse_speed_base: float = 1.0           # multiplier
    mouse_overshoot_rate: float = 0.15      # probability of overshoot
    mouse_jitter: float = 0.02              # random micro-movements
    click_delay_range: Tuple[float, float] = (0.05, 0.15)
    
    # Scrolling
    scroll_speed: float = 1.0
    scroll_pause_probability: float = 0.1
    scroll_pause_duration: Tuple[float, float] = (0.5, 2.0)
    
    # Reading/Thinking
    read_speed_wpm: float = 200.0
    think_ratio: float = 0.3                # fraction of time "thinking" vs acting
    distraction_rate: float = 0.05          # random tab switch, window focus loss
    
    # Session
    max_session_minutes: float = 45.0
    break_duration_range: Tuple[float, float] = (30.0, 120.0)  # seconds
    
    @classmethod
    def random(cls, seed: Optional[int] = None) -> "BehaviorProfile":
        """Generate a realistic random profile."""
        rng = random.Random(seed)
        return cls(
            typing_speed_wpm=rng.uniform(40, 80),
            typing_variance=rng.uniform(0.2, 0.5),
            typo_rate=rng.uniform(0.01, 0.05),
            typo_correction_delay=(rng.uniform(0.05, 0.2), rng.uniform(0.3, 0.8)),
            mouse_speed_base=rng.uniform(0.8, 1.3),
            mouse_overshoot_rate=rng.uniform(0.1, 0.25),
            mouse_jitter=rng.uniform(0.01, 0.05),
            click_delay_range=(rng.uniform(0.03, 0.1), rng.uniform(0.1, 0.25)),
            scroll_speed=rng.uniform(0.7, 1.4),
            scroll_pause_probability=rng.uniform(0.05, 0.15),
            scroll_pause_duration=(rng.uniform(0.3, 1.0), rng.uniform(1.0, 3.0)),
            read_speed_wpm=rng.uniform(150, 300),
            think_ratio=rng.uniform(0.2, 0.5),
            distraction_rate=rng.uniform(0.02, 0.1),
            max_session_minutes=rng.uniform(30, 90),
            break_duration_range=(rng.uniform(20, 60), rng.uniform(60, 300)),
        )


class HumanTyping:
    """Human-like typing with errors and corrections."""
    
    def __init__(self, profile: BehaviorProfile, rng: random.Random):
        self.profile = profile
        self.rng = rng
        self.chars_per_second = profile.typing_speed_wpm * 5 / 60  # ~5 chars per word
    
    async def type(self, page: Page, selector: str, text: str, clear_first: bool = True):
        """Type text into element with human behavior."""
        element = await page.wait_for_selector(selector)
        
        if clear_first:
            await element.click()
            await page.keyboard.press("Control+A")
            await asyncio.sleep(0.1)
        
        for i, char in enumerate(text):
            # Random typo
            if self.rng.random() < self.profile.typo_rate and char.isalpha():
                wrong_char = self.rng.choice("abcdefghijklmnopqrstuvwxyz")
                await page.keyboard.type(wrong_char)
                await asyncio.sleep(self.rng.uniform(*self.profile.typo_correction_delay))
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.05)
            
            await page.keyboard.type(char)
            
            # Variable delay between keystrokes
            base_delay = 1.0 / self.chars_per_second
            variance = self.profile.typing_variance
            delay = base_delay * self.rng.uniform(1 - variance, 1 + variance)
            await asyncio.sleep(delay)
        
        # Small pause after finishing
        await asyncio.sleep(self.rng.uniform(0.2, 0.5))


class HumanMouse:
    """Human-like mouse movements using Bezier curves."""
    
    def __init__(self, profile: BehaviorProfile, rng: random.Random):
        self.profile = profile
        self.rng = rng
        self.current_pos = (0, 0)
    
    def _bezier_point(self, t: float, p0: Tuple[float, float], p1: Tuple[float, float], 
                      p2: Tuple[float, float], p3: Tuple[float, float]) -> Tuple[float, float]:
        """Cubic Bezier curve point."""
        u = 1 - t
        uu = u * u
        uuu = uu * u
        tt = t * t
        ttt = tt * t
        
        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return (x, y)
    
    def _generate_curve(self, start: Tuple[float, float], end: Tuple[float, float], 
                        steps: int = 20) -> List[Tuple[float, float]]:
        """Generate human-like mouse curve."""
        # Control points for natural curve
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        
        # Add randomness to control points
        offset = self.rng.uniform(-50, 50)
        cp1 = (mid_x + offset, start[1] + self.rng.uniform(-30, 30))
        cp2 = (mid_x - offset, end[1] + self.rng.uniform(-30, 30))
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            point = self._bezier_point(t, start, cp1, cp2, end)
            # Add micro-jitter
            jitter = self.profile.mouse_jitter
            point = (point[0] + self.rng.uniform(-jitter, jitter) * 10,
                     point[1] + self.rng.uniform(-jitter, jitter) * 10)
            points.append(point)
        return points
    
    async def move_to(self, page: Page, target_x: float, target_y: float):
        """Move mouse to target with human curve."""
        start = self.current_pos
        end = (target_x, target_y)
        
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        steps = max(10, int(distance / 10 * self.profile.mouse_speed_base))
        
        curve = self._generate_curve(start, end, steps)
        
        for point in curve:
            await page.mouse.move(point[0], point[1])
            await asyncio.sleep(0.005 * self.profile.mouse_speed_base)
        
        # Overshoot correction
        if self.rng.random() < self.profile.mouse_overshoot_rate:
            overshoot_x = end[0] + self.rng.uniform(-10, 10)
            overshoot_y = end[1] + self.rng.uniform(-10, 10)
            await page.mouse.move(overshoot_x, overshoot_y)
            await asyncio.sleep(0.05)
            await page.mouse.move(end[0], end[1])
        
        self.current_pos = end
    
    async def click(self, page: Page, x: float = None, y: float = None):
        """Human-like click with pre-click delay."""
        if x is not None and y is not None:
            await self.move_to(page, x, y)
        
        # Pre-click pause
        await asyncio.sleep(self.rng.uniform(*self.profile.click_delay_range))
        await page.mouse.down()
        await asyncio.sleep(self.rng.uniform(0.02, 0.08))
        await page.mouse.up()


class HumanScroll:
    """Human-like scrolling behavior."""
    
    def __init__(self, profile: BehaviorProfile, rng: random.Random):
        self.profile = profile
        self.rng = rng
    
    async def scroll_page(self, page: Page, direction: str = "down", 
                          distance: Optional[float] = None):
        """Scroll with human pauses and variable speed."""
        if distance is None:
            distance = self.rng.uniform(300, 800)
        
        steps = int(distance / 50)
        for _ in range(steps):
            delta = self.rng.uniform(30, 70) * self.profile.scroll_speed
            if direction == "down":
                await page.mouse.wheel(0, delta)
            else:
                await page.mouse.wheel(0, -delta)
            
            await asyncio.sleep(self.rng.uniform(0.05, 0.15) / self.profile.scroll_speed)
            
            # Random pause
            if self.rng.random() < self.profile.scroll_pause_probability:
                await asyncio.sleep(self.rng.uniform(*self.profile.scroll_pause_duration))
    
    async def scroll_to_element(self, page: Page, selector: str):
        """Scroll until element is visible."""
        element = await page.wait_for_selector(selector)
        box = await element.bounding_box()
        if box:
            # Scroll to element center
            await page.evaluate(f"""
                window.scrollTo({{
                    top: {box['y'] - 200},
                    behavior: 'smooth'
                }});
            """)
            await asyncio.sleep(self.rng.uniform(0.5, 1.5))


class HumanBehavior:
    """Orchestrates all human behaviors for a session."""
    
    def __init__(self, profile: BehaviorProfile, rng: random.Random):
        self.profile = profile
        self.rng = rng
        self.typing = HumanTyping(profile, self.rng)
        self.mouse = HumanMouse(profile, self.rng)
        self.scroll = HumanScroll(profile, self.rng)
        self.session_start = None
        self.action_count = 0
    
    async def start_session(self):
        self.session_start = asyncio.get_event_loop().time()
    
    async def should_break(self) -> bool:
        """Check if session should take a break."""
        if not self.session_start:
            return False
        elapsed = asyncio.get_event_loop().time() - self.session_start
        return elapsed > self.profile.max_session_minutes * 60
    
    async def think_pause(self):
        """Simulate thinking/reading pause."""
        if self.rng.random() < self.profile.think_ratio:
            pause = self.rng.uniform(1.0, 5.0)
            await asyncio.sleep(pause)
    
    async def maybe_distract(self, page: Page):
        """Random distraction (tab switch, focus loss)."""
        if self.rng.random() < self.profile.distraction_rate:
            # Blur/focus window
            await page.evaluate("window.blur()")
            await asyncio.sleep(self.rng.uniform(0.5, 2.0))
            await page.evaluate("window.focus()")
            await asyncio.sleep(self.rng.uniform(0.2, 0.5))
    
    async def read_text(self, page: Page, selector: str) -> str:
        """Simulate reading text on page."""
        element = await page.wait_for_selector(selector)
        text = await element.inner_text()
        
        # Calculate reading time
        words = len(text.split())
        read_time = (words / self.profile.read_speed_wpm) * 60
        read_time *= self.rng.uniform(0.8, 1.2)  # variance
        
        # Scroll through if long
        if words > 100:
            await self.scroll.scroll_to_element(page, selector)
        
        await asyncio.sleep(min(read_time, 10.0))  # Cap at 10s
        return text
    
    async def fill_form(self, page: Page, fields: dict):
        """Fill multiple form fields with human behavior."""
        for selector, value in fields.items():
            await self.think_pause()
            await self.mouse.click(page)
            await self.typing.type(page, selector, value)
            await asyncio.sleep(self.rng.uniform(0.2, 0.5))
    
    async def click_element(self, page: Page, selector: str):
        """Click with human mouse movement."""
        element = await page.wait_for_selector(selector)
        box = await element.bounding_box()
        if box:
            center_x = box['x'] + box['width'] / 2
            center_y = box['y'] + box['height'] / 2
            await self.mouse.move_to(page, center_x, center_y)
            await self.mouse.click(page)
        else:
            await element.click()


# =============================================================================
# TEST
# =============================================================================

def test_behavior_profile():
    """Test behavior profile generation."""
    print("=== BEHAVIOR PROFILE TEST ===")
    
    for i in range(3):
        profile = BehaviorProfile.random(seed=42 + i)
        print(f"\nProfile {i+1}:")
        print(f"  Typing: {profile.typing_speed_wpm:.0f} WPM ±{profile.typing_variance*100:.0f}%")
        print(f"  Mouse: {profile.mouse_speed_base:.2f}x, overshoot {profile.mouse_overshoot_rate*100:.0f}%")
        print(f"  Scroll: {profile.scroll_speed:.2f}x, pause {profile.scroll_pause_probability*100:.0f}%")
        print(f"  Think ratio: {profile.think_ratio*100:.0f}%")
        print(f"  Session: {profile.max_session_minutes:.0f} min")


if __name__ == "__main__":
    test_behavior_profile()