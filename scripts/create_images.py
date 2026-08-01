#!/usr/bin/env python3
"""Create placeholder images for the 5 prepared posts"""
from PIL import Image, ImageDraw, ImageFont
import os

images_dir = 'D:/Portable_Soft/hermes/assets/content_warehouse/images'
os.makedirs(images_dir, exist_ok=True)

posts = [
    ('post1_problem_solution.png', 'Problem → Solution', 'Stop Manual Offer Hunting\nSave 10 hours/week', '#2E86AB'),
    ('post2_before_after.png', 'Before → After', '20 hrs/month saved\non trend monitoring', '#A23B72'),
    ('post3_mistake.png', 'Mistake Analysis', 'Lost $200 on TikTok Ads\nin 48h - Lessons Learned', '#F18F01'),
    ('post4_tool_closeup.png', 'Tool Close-up', 'Fal.ai — GPU inference\nfor $0.003/pin', '#C73E1D'),
    ('post5_top3_comparison.png', 'Top 3 AI Tools 2025', 'Real Comparison:\nBing vs Leonardo vs Playground', '#2E86AB'),
]

channels = ['@max_brain_chef_official', '@ai_frontier_you', '@max_brain_chef_ai', '@neuro_kitchen_ai']

for filename, title, subtitle, color in posts:
    img = Image.new('RGB', (1200, 675), color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a font
    try:
        font_title = ImageFont.truetype('arial.ttf', 52)
        font_sub = ImageFont.truetype('arial.ttf', 30)
        font_ch = ImageFont.truetype('arial.ttf', 18)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_ch = ImageFont.load_default()
    
    # Draw title
    bbox = draw.textbbox((0, 0), title, font=font_title)
    w = bbox[2] - bbox[0]
    draw.text(((1200-w)//2, 200), title, fill='white', font=font_title)
    
    # Draw subtitle (multiline)
    lines = subtitle.split('\n')
    y = 280
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        w = bbox[2] - bbox[0]
        draw.text(((1200-w)//2, y), line, fill='white', font=font_sub)
        y += 40
    
    # Add channel handles at bottom
    ch_text = '  |  '.join(channels)
    bbox = draw.textbbox((0, 0), ch_text, font=font_ch)
    w = bbox[2] - bbox[0]
    draw.text(((1200-w)//2, 620), ch_text, fill='white', font=font_ch)
    
    # Add decorative elements - corners
    draw.rectangle([0, 0, 1200, 675], outline='white', width=3)
    
    filepath = os.path.join(images_dir, filename)
    img.save(filepath, 'PNG', quality=95)
    print(f'Created: {filepath}')

print(f'\nAll 5 images created in {images_dir}')