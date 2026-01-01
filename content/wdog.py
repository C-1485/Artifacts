from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import sys

if len(sys.argv) != 2:
    print("Usage: python watch_screenshots_append.py <ReportName>")
    sys.exit(1)

BASE = Path(__file__).parent
NAME = sys.argv[1]

IMG_DIR = BASE / f"captures/screens/{NAME}"
MD_FILE = BASE / f"captures/{NAME}.md"

if not IMG_DIR.exists():
    print(f"[!] Screenshot directory not found: {IMG_DIR}")
    sys.exit(1)

if not MD_FILE.exists():
    print(f"[!] Markdown file not found: {MD_FILE}")
    sys.exit(1)

ANCHOR = "<!-- screenshots:anchor -->"

def append_image_block(image_path):
    """Append a new block for a screenshot if not already in the Markdown."""
    md_text = MD_FILE.read_text()
    image_name = image_path.stem

    # Check if image is already documented
    if f"](/captures/screens/{NAME}/{image_name}.png)" in md_text:
        return False

    # Create Markdown block
    rel_path = image_path.relative_to(BASE)
    block = f"\n### {image_name}\n![{image_name}](/{rel_path})\n\n**Description:**\n_TODO_\n"

    # Insert after anchor
    if ANCHOR in md_text:
        new_text = md_text.replace(ANCHOR, ANCHOR + block)
    else:
        # fallback: append at end
        new_text = md_text + "\n" + block

    MD_FILE.write_text(new_text)
    print(f"[+] Appended {image_name} to {MD_FILE.name}")
    return True

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".png"):
            # Wait to ensure file is fully written
            time.sleep(0.3)
            append_image_block(Path(event.src_path))

observer = Observer()
observer.schedule(Handler(), IMG_DIR, recursive=False)
observer.start()

print(f"[*] Watching screenshots in: {IMG_DIR}")
print(f"[*] Add new screenshots and they will be appended to {MD_FILE.name}")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
