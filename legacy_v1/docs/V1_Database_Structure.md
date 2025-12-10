# SmartSorter Pro V1 â€” Database Structure

V1 used a temporary SQLite database for metadata storage.

## Table: faces
- id (INTEGER)
- file_path (TEXT)
- embedding (BLOB)
- created_at (TEXT)

## Table: files
- id (INTEGER)
- file_path (TEXT)
- hash (TEXT)
- type (TEXT)
- date_taken (TEXT)

This DB will be redesigned in V2 as a pluggable provider.
