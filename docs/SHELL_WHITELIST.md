# Shell Command Whitelist — MCP-Agent Security Policy

## Überblick

Die Shell-Integration des MCP-Agents folgt einem **Whitelist-basiertem Sicherheitsmodell**:
- ✅ Nur explizit erlaubte Befehle können ausgeführt werden
- ❌ Alle nicht in der Allowlist aufgeführten Befehle werden blockiert
- 🛑 Zusätzlich blockierte Muster für hochriskante Operationen

## Erlaubte Befehlskategorien

### 1. Navigation & Verzeichnisse
```
pwd       # Aktuelles Verzeichnis anzeigen
ls        # Verzeichnis auflisten
dir       # Verzeichnis auflisten (Windows)
mkdir     # Verzeichnis erstellen
rmdir     # Leeres Verzeichnis löschen
find      # Dateien suchen
```

**Einschränkung**: `cd` funktioniert nicht (ist nur für interaktive Shells relevant)

### 2. Dateiverwaltung & Lesen
```
cat       # Dateiinhalt lesen
head      # Erste Zeilen
tail      # Letzte Zeilen
grep      # In Dateien suchen
wc        # Zählen (Zeilen, Wörter, Bytes)
file      # Dateityp bestimmen
diff      # Dateien vergleichen
touch     # Datei erstellen/aktualisieren
cp        # Datei kopieren (nur project-intern)
mv        # Datei verschieben (nur project-intern)
```

**Einschränkung**: Nur innerhalb des Projekt-Verzeichnisses

### 3. Entwickler-Tools
```
git       # Version Control (alle subcommands)
python    # Python 2
python3   # Python 3
pip       # Python Package Manager
pip3      # Python 3 Package Manager
node      # Node.js Runtime
npm       # Node Package Manager
cargo     # Rust Package Manager
docker    # Container Runtime (aber keine rm/delete)
```

**Einschränkung**: Docker destructive operations (`rm`, `rmi`, `delete`) sind blockiert

### 4. System-Information
```
whoami    # Aktueller Benutzer
date      # Aktuelle Zeit
hostname  # Rechner-Name
uname     # System-Information
echo      # Text ausgeben
which     # Befehl-Pfad
type      # Befehls-Typ
sort      # Sortieren
uniq      # Duplikate entfernen
test      # Bedingte Tests
chmod     # Datei-Berechtigungen (begrenzt)
```

## Blockierte Muster (Gefährliche Operationen)

Folgende Patterns werden unabhängig vom Basis-Befehl blockiert:

| Pattern | Grund | Alternative |
|---------|-------|-------------|
| `rm -rf` | Rekursives Löschen | einzeln löschen |
| `rm -r /` | Root löschen | Nicht erlaubt |
| `del /s` | Rekursiv löschen (Windows) | Nicht erlaubt |
| `mkfs` | Dateisystem formatieren | Nicht erlaubt |
| `fdisk` | Festplatte partitionieren | Nicht erlaubt |
| `dd if=/dev` | Raw-Disk-Operationen | Nicht erlaubt |
| `shutdown` | System herunterfahren | Nicht erlaubt |
| `reboot` | System neustart | Nicht erlaubt |
| `poweroff` | Ausschalten | Nicht erlaubt |
| `passwd` | Passwort ändern | Nicht erlaubt |
| `useradd` | Benutzer hinzufügen | Nicht erlaubt |
| `systemctl` | Service starten/stoppen | Nicht erlaubt |
| `iptables` | Firewall ändern | Nicht erlaubt |

## Safety Features

### 1. **Command Base Validation**
```
"python script.py"  ✅ Erlaubt (python ist in ALLOWED)
"rm script.py"      ❌ Blockiert (rm nicht in ALLOWED)
"cp file.txt x"     ✅ Erlaubt (aber nur wenn in project dir)
```

### 2. **Pattern Blocking**
```
"rm -rf /"          ❌ Blockiert ("rm -rf" ist blocked pattern)
"sudo bash"         ❌ Blockiert ("sudo" nicht in ALLOWED)
```

### 3. **Working Directory Restriction**
```
cp /etc/passwd .          ❌ Blockiert (source außerhalb project)
cp data/file.txt backup/  ✅ Erlaubt (alles innerhalb project)
```

### 4. **Timeout Protection**
```
Alle Befehle:  30 Sekunden max
Längere Tasks: ❌ Blockiert ("Timeout (30s überschritten)")
```

### 5. **Output Size Limiting**
```
Maximale Output: 5000 Zeichen
Große Outputs:   Automatisch gekürzt (mit Info)
```

### 6. **CWD Security**
```
Alle Befehle laufen nur im aktuellen Projekt-Verzeichnis
```

## Praktische Beispiele

### ✅ Erlaubte Befehle
```bash
# Dateioperationen
ls -la
cat config.json
grep "TODO" src/**/*.py
find . -name "*.py"

# Entwicklung
python -m pytest tests/
python3 --version
pip install requests

# Git
git status
git log --oneline

# System Info
whoami
date
pwd
```

### ❌ Blockierte Befehle
```bash
# Destruktiv
rm -rf /var/log
dd if=/dev/sda1

# Privilegien
sudo apt install vim
passwd root

# Systemkontrolle
reboot
shutdown -h now

# Nicht whitelisted
vim file.txt
docker rm -f container
```

## Erweiterung der Allowlist

Falls Sie einen neuen Befehl brauchen:

1. **Sicherheit bewerten**: Ist der Befehl destruktiv?
2. **Risiko minimieren**: Addieren Sie Pattern-Blockierungen statt Base-Commands?
3. **Eintrag erstellen**: In [tools/shell.py](../tools/shell.py) zur richtigen Kategorie hinzufügen
4. **Tests aktualisieren**: [test_agent_pytest.py](../test_agent_pytest.py) - `TestShell` Klasse
5. **Dokumentation**: Dieses Dokument aktualisieren

### Template für neue Befehle
```python
# In SAFE_[CATEGORY]_COMMANDS:
"newcommand",  # Description of what this does
```

## Auditieren der Shell Konfiguration

```bash
# Alle erlaubten Befehle sehen:
grep -E "ALLOWED_COMMANDS|SAFE_.*_COMMANDS" tools/shell.py

# Alle blockierten Muster sehen:
grep -E "BLOCKED_PATTERNS" tools/shell.py

# Tests ausführen:
pytest test_agent_pytest.py::TestShell -v
```

## Sicherheitshinweise

⚠️ **Wichtig**: Diese Whitelist schützt vor **unbeabsichtigten** Problemen, nicht vor **böswilligen** Attacken. Der Agent sollte immer in einer isolierten Umgebung laufen.

🔒 **Best Practices**:
1. Immer auf einem sauberen System testen
2. Git-Repos regelmäßig backen
3. Container/VMs für kritische Operationen verwenden
4. Output der Befehle überprüfen
5. Logs für Audit-Trail führen
