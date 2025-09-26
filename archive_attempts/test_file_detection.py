# test_file_detection.py
import glob
import os

print("Files in directory:")
for f in os.listdir('.'):
    if '.json' in f:
        print(f"  - {f}")

print("\nFiles matching 'jobs_*.json':")
files = glob.glob('jobs_*.json')
for f in files:
    print(f"  - {f}")

print("\nLatest file would be:")
if files:
    print(f"  - {sorted(files)[-1]}")
else:
    print("  - No matching files found!")