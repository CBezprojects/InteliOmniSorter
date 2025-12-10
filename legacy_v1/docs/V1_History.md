# SmartSorter Pro â€” V1 History

SmartSorter began as a personal automation tool designed to solve a practical problem:
sorting thousands of photos, screenshots, downloads, and mixed-format files distributed
across multiple drives. Over time, the tool evolved into a semi-modular system with
PowerShell automation, Python-based logic, and a set of convenience scripts created
incrementally to handle real-world file chaos.

V1 was not designed upfront as a unified product. It grew reactively, responding to
day-by-day needs:

- Clean a folder with 10 000+ mixed files
- Sort images by date and similarity
- Create structured destination folders
- Track which files moved where
- Keep logs for reversibility
- Add optional face detection
- Add auto-mount for phones and USB devices
- Run the pipeline from a single script

As the capabilities increased, SmartSorter Pro V1 became a hybrid system:

- PowerShell (for automation, scanning, logging)
- Python (for face detection & similarity clustering)
- dlib / face_recognition (for embeddings)
- SQLite (for temporary file metadata storage)
- CSV logs for tracking each run

By late V1, the system was powerfulâ€”but fragmented, inconsistent, and difficult to extend.

The decision was made to freeze V1 and create InteliOmniSorter V2, a unified,
modular, modern version that inherits the ideas but not the legacy complexity.
