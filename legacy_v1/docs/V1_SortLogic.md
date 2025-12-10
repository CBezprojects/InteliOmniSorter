# SmartSorter Pro V1 â€” Sorting Logic Overview

Sorting followed a sequential decision chain:

## 1. Identify File Type
Based on extension/MIME.

## 2. Extract Metadata
EXIF timestamps, device model, orientation.

## 3. Compute Destination Folder
Examples:
- Images â†’ Photos/YYYY/MM-DD
- Videos â†’ Videos/YYYY/MM-DD
- Screenshots â†’ Screenshots/YYYY-MM
- Documents â†’ Documents/
- Unknown â†’ Misc/

## 4. Apply Optional Face Clustering
Distance thresholds:
- <0.45 â†’ same person
- 0.45â€“0.6 â†’ maybe
- >0.6 â†’ different

## 5. Move Files Safely
Ensures no overwrites.

## 6. Write Logs
CSV logs allow reversibility.

This becomes the foundation for V2â€™s sort_engine.py.
