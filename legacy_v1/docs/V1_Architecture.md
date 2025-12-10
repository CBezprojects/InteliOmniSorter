# SmartSorter Pro V1 â€” Architecture Overview

V1 architecture consisted of loosely connected modules and scripts without a unified
framework. It worked, but lacked cohesion and scalability.

## 1. PowerShell Automation Layer
- Entry point for running the sorter
- Folder scanning
- Routing logic
- Logging
- Menu display

## 2. Python Processing Layer
- face_recognition + dlib embeddings
- Facial similarity clustering
- Lightweight sort engine
- SQLite temporary DB

## 3. File Classification Logic
Sorting was based on:
- Extension
- MIME type
- Date created/modified
- EXIF metadata
- Optional faces

## 4. Logging System
- CSV logs per run
- Reversible operations

## 5. Auto-Mount System
- Polling-based detection
- Pulls from DCIM or removable storage

## 6. Face Engine
- Embedding extraction
- Euclidean distance similarity

---

## Architectural Issues
- No plugin system
- Tight coupling between PowerShell & Python
- Hard to package
- No GUI framework
- Inconsistent folder structure
