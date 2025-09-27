#!/usr/bin/env python3
import sys
print('Python executable:', sys.executable)
print('Python version:', sys.version)
print('\nPython path:')
for p in sys.path:
    print(f'  {p}')

print('\nTrying to import anthropic...')
try:
    import anthropic
    print('✅ SUCCESS! anthropic imported')
    print(f'   Version: {anthropic.__version__}')
    print(f'   Location: {anthropic.__file__}')
except ImportError as e:
    print(f'❌ FAILED! ImportError: {e}')
except Exception as e:
    print(f'❌ FAILED! {type(e).__name__}: {e}')

print('\nTrying to import analyzer_ai...')
try:
    from analyzer_ai import AIJobAnalyzer
    print('✅ analyzer_ai imported')
except Exception as e:
    print(f'❌ Failed to import analyzer_ai: {e}')
    import traceback
    traceback.print_exc()
