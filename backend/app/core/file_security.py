import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded filename to prevent directory traversal or unsafe execution.
    Only allows alphanumeric characters, underscores, hyphens, and single dots.
    """
    # Extract only the base name (strip any path components)
    basename = Path(filename).name
    # Replace non-whitelisted characters with underscore
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', basename)
    # Strip leading/trailing dots or underscores
    clean = clean.strip('._')
    if not clean:
        clean = "uploaded_document"
    return clean
