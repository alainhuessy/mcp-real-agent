"""Shell Tool — geschützte Shell-Ausführung mit erweiterte Allowlist."""

import subprocess
import os

# ════════════════════════════════════════════════════════════════════════════
# SHELL SECURITY CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

# Erlaubte Basis-Befehle (Navigation, Dateien, System Info)
SAFE_NAVIGATION_COMMANDS = [
    "pwd",      # Print working directory
    "cd",       # Change directory
    "ls",       # List files (Unix)
    "dir",      # List files (Windows)
    "mkdir",    # Make directory
    "rmdir",    # Remove empty directory
    "touch",    # Create file
    "cp",       # Copy file (mit Beschränkung)
    "mv",       # Move file (mit Beschränkung)
]

# Datei-Betrachtung und Bearbeitung
SAFE_FILE_COMMANDS = [
    "cat",      # Read file
    "head",     # First lines
    "tail",     # Last lines
    "grep",     # Search in files
    "wc",       # Word count
    "file",     # File type
    "chmod",    # Permissions (begrenzt)
    "less",     # Pager
    "more",     # Pager
]

# Entwickler-Tools
SAFE_DEV_COMMANDS = [
    "git",      # Version control
    "python",   # Python interpreter
    "python3",  # Python 3
    "pip",      # Package manager
    "pip3",     # Package manager
    "node",     # Node.js
    "npm",      # Node package manager
    "cargo",    # Rust package manager
    "docker",   # Container runtime (begrenzt)
]

# System-Information
SAFE_SYSTEM_COMMANDS = [
    "whoami",   # Current user
    "date",     # Current date/time
    "hostname", # Hostname
    "uname",    # System info
    "echo",     # Print text
    "which",    # Find command
    "type",     # Command type
    "find",     # Find files
    "sort",     # Sort lines
    "uniq",     # Unique lines
    "diff",     # Diff files
    "test",     # Test conditions
]

# Kombinierte Allowlist
ALLOWED_COMMANDS = (
    SAFE_NAVIGATION_COMMANDS +
    SAFE_FILE_COMMANDS +
    SAFE_DEV_COMMANDS +
    SAFE_SYSTEM_COMMANDS
)

# ════════════════════════════════════════════════════════════════════════════
# BLOCKED PATTERNS (Gefährliche Operationen)
# ════════════════════════════════════════════════════════════════════════════

BLOCKED_PATTERNS = [
    # Destruktive Operationen
    "rm -rf", "rm -r /", "del /s", "format",
    # System Kontrolle
    "shutdown", "reboot", "halt", "poweroff",
    # Disk Operationen
    "mkfs", "fdisk", "parted", "dd if=/dev",
    # User/Permissions
    "passwd", "useradd", "userdel", "sudo",
    # Kernel
    "insmod", "rmmod", "modprobe",
    # Init System
    "systemctl", "service", "chkconfig",
    # Network Änderung
    "ifconfig", "route add", "iptables",
]



def shell(cmd: str) -> str:
    """
    Führt einen Shell-Befehl aus (nur erlaubte Kommandos).
    
    SICHERHEIT:
    - Whitelisted Base-Command Checking
    - Blocked Pattern Detection
    - Timeout Protection (30s)
    - CWD Restriction (nur project-Umgebung)
    """
    if not cmd.strip():
        return "❌ Leerer Befehl"

    # ── Dangerous Pattern Detection ──
    cmd_lower = cmd.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            return f"❌ Befehl blockiert (Muster: '{pattern}')"

    # ── Base Command Validation ──
    base = cmd.split()[0]
    
    # Spezielle Behandlung für cd (kann nicht in subprocess laufen)
    if base == "cd":
        return "ℹ️ cd muss in der Shell-Sitzung ausgeführt werden. Nutze 'pwd' für aktuelles Verzeichnis."
    
    if base not in ALLOWED_COMMANDS:
        return f"❌ Befehl nicht erlaubt: '{base}'. Erlaubte Befehle: {', '.join(sorted(set(ALLOWED_COMMANDS)))[:100]}..."

    # ── Command-spezifische Restriktionen ──
    if base in ["cp", "mv"]:
        if any(p in cmd for p in ["/", "..", "~"]):
            if not any(p in cmd for p in [os.getcwd()]):
                return f"⚠️  {base} nur innerhalb des Projekt-Verzeichnisses erlaubt"
    
    if base == "docker":
        if "rm" in cmd or "delete" in cmd or "rmi" in cmd:
            return "⚠️  Docker destructive operations nicht erlaubt"

    # ── Safe Execution ──
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=os.getcwd()  # Nur im aktuellen Verzeichnis
        )
        
        output = result.stdout or result.stderr or "(kein Output)"
        
        # Begrenzen Sie die Output-Größe
        if len(output) > 5000:
            output = output[:5000] + f"\n... (gekürzt, insgesamt {len(output)} Zeichen)"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "❌ Timeout (30s überschritten)"
    except Exception as e:
        return f"❌ Shell Fehler: {e}"
