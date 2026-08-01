#!/usr/bin/env python3
"""YouTube Transcript Extractor — Hermes Stealth Browser Toolkit

Usage:
    python scripts/youtube_transcript.py VIDEO_ID [--lang en] [--proxy http://127.0.0.1:10806]

Output: JSON with transcript segments + metadata

Requires: pip install youtube-transcript-api
"""
import os, sys, json, argparse

def main():
    parser = argparse.ArgumentParser(description='Extract YouTube transcript')
    parser.add_argument('video_id', help='YouTube video ID')
    parser.add_argument('--lang', default='en', help='Language code (default: en)')
    parser.add_argument('--proxy', default='http://127.0.0.1:10806',
                        help='Proxy URL (default: http://127.0.0.1:10806)')
    args = parser.parse_args()

    # Set proxy
    os.environ['http_proxy'] = args.proxy
    os.environ['https_proxy'] = args.proxy

    from youtube_transcript_api import YouTubeTranscriptApi

    api = YouTubeTranscriptApi()
    transcript = api.fetch(args.video_id, languages=[args.lang])
    segments = list(transcript)

    result = {
        'video_id': args.video_id,
        'language': transcript.language_code,
        'is_generated': transcript.is_generated,
        'segments': len(segments),
        'snippets': [
            {'text': s.text, 'start': s.start, 'duration': s.duration}
            for s in segments
        ]
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
