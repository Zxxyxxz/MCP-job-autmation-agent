#!/usr/bin/env python3
"""
AI-Powered Job Search Agent
Main entry point for the application.

Usage:
    python main.py                          # Full pipeline with defaults
    python main.py --skip-enrich            # Skip Selenium enrichment step
    python main.py --queries "AI engineer"  # Custom search queries
    python main.py --no-headless            # Show browser windows (default: headless)
    python main.py scrape                   # Scrape only
    python main.py enrich                   # Enrich only
    python main.py analyze                  # Analyze only
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from run_pipeline import JobPipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description='AI-Powered LinkedIn Job Search Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  python main.py                           # Full pipeline\n'
               '  python main.py scrape --queries "AI"      # Scrape only\n'
               '  python main.py enrich --limit 10          # Enrich 10 jobs\n'
               '  python main.py analyze                    # Analyze all\n'
               '  python main.py --no-headless              # Show browser\n',
    )

    parser.add_argument(
        'command', nargs='?', default='full',
        choices=['full', 'scrape', 'enrich', 'analyze'],
        help='Pipeline step to run (default: full)',
    )
    parser.add_argument(
        '--queries', '-q', nargs='+',
        help='Search queries (default: built-in list)',
    )
    parser.add_argument(
        '--location', '-l', default='Netherlands',
        help='Job location filter (default: Netherlands)',
    )
    parser.add_argument(
        '--skip-enrich', action='store_true',
        help='Skip Selenium-based description enrichment',
    )
    parser.add_argument(
        '--no-headless', action='store_true',
        help='Show browser windows instead of running headless',
    )
    parser.add_argument(
        '--limit', type=int, default=20,
        help='Max jobs to enrich/analyze per run (default: 20)',
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable debug logging',
    )

    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    pipeline = JobPipeline(headless=not args.no_headless)

    if args.command == 'scrape':
        pipeline.scrape(args.queries or pipeline._default_queries(), args.location)
    elif args.command == 'enrich':
        pipeline.enrich(limit=args.limit)
    elif args.command == 'analyze':
        pipeline.analyze(limit=args.limit)
    else:
        pipeline.run_full_pipeline(
            queries=args.queries,
            location=args.location,
            skip_enrich=args.skip_enrich,
        )


if __name__ == '__main__':
    main()
