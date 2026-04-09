import os
from pathlib import Path

# Basic path configuration
VAULT_DIR = Path.home() / ".vlt"
VAULT_FILE = VAULT_DIR / "vault.vlt"

def get_vlt_path() -> Path:
    """Obtain and ensure that the ~/.vlt directory exists."""
    if not VAULT_DIR.exists():
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        if os.name != 'nt':
            os.chmod(VAULT_DIR, 0o700)
    return VAULT_DIR

def get_vault_file() -> Path:
    """Return to vault file path"""
    return VAULT_FILE

def ensure_storage_path():
    """Initialize storage environment"""
    get_vlt_path()

def vault_exists() -> bool:
    """Check if the vault documents exist and are valid."""
    return VAULT_FILE.is_file()

def write_vault_raw(content: str):
    """Write the raw string (usually encrypted Base64 data)."""
    ensure_storage_path()
    VAULT_FILE.write_text(content, encoding="utf-8")
    if os.name != 'nt':
        os.chmod(VAULT_FILE, 0o600)

def read_vault_raw() -> str:
    """Read raw string data"""
    if not vault_exists():
        return ""
    return VAULT_FILE.read_text(encoding="utf-8")

# --- Compatibility wrapper (if your old code calls these names) ---

def write_vault(content: str):
    write_vault_raw(content)

def read_vault() -> str:
    return read_vault_raw()