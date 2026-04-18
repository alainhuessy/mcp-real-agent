"""Logger System für Agent OS v2.1 — Detailliertes Logging mit Levels."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class AgentLogger:
    """Professional Logging System für Agent OS."""
    
    def __init__(self, name: str = "agent-os", log_dir: str = "logs"):
        """Initialize Agent Logger with file and console handlers.
        
        Args:
            name: Logger name (default: agent-os)
            log_dir: Directory for log files (default: logs/)
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Logger setup
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Handler: File + Console
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Erstelle File und Console Handler."""
        
        # Format
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] [%(component)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console Handler (nur WARN + ERROR)
        console = logging.StreamHandler(sys.stderr)
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        self.logger.addHandler(console)
        
        # File Handler (alle Logs)
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = self.log_dir / f"agent-{today}.log"
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error File Handler (nur Errors)
        error_path = self.log_dir / f"errors-{today}.log"
        error_handler = logging.FileHandler(error_path)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def _log(self, level: int, component: str, message: str):
        """Interne Logging Methode."""
        extra = {"component": component}
        self.logger.log(level, message, extra=extra)
    
    # ── Public API ────────────────────────────────────────────────
    
    def debug(self, component: str, message: str):
        """Debug Level — Detaillierte Info."""
        self._log(logging.DEBUG, component, message)
    
    def info(self, component: str, message: str):
        """Info Level — Standard Info."""
        self._log(logging.INFO, component, message)
    
    def warning(self, component: str, message: str):
        """Warning Level — Warnung."""
        self._log(logging.WARNING, component, message)
    
    def error(self, component: str, message: str, exception: Optional[Exception] = None):
        """Error Level — Kritischer Fehler."""
        if exception:
            message += f"\n{type(exception).__name__}: {str(exception)}"
        self._log(logging.ERROR, component, message)
    
    def critical(self, component: str, message: str):
        """Critical Level — System Fehler."""
        self._log(logging.CRITICAL, component, message)


# ──── Global Logger Instance ────────────────────────────────────

_logger_instance: Optional[AgentLogger] = None


def get_logger() -> AgentLogger:
    """Gibt die globale Logger-Instanz zurück."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AgentLogger()
    return _logger_instance


# ──── Convenience Functions ────────────────────────────────────

def log_debug(component: str, message: str):
    """Shortcut: Log debug message."""
    get_logger().debug(component, message)


def log_info(component: str, message: str):
    """Shortcut: Log info message."""
    get_logger().info(component, message)


def log_warning(component: str, message: str):
    """Shortcut: Log warning message."""
    get_logger().warning(component, message)


def log_error(component: str, message: str, exception: Optional[Exception] = None):
    """Shortcut: Log error message."""
    get_logger().error(component, message, exception)


def log_critical(component: str, message: str):
    """Shortcut: Log critical message."""
    get_logger().critical(component, message)


# ──── Context Managers ────────────────────────────────────────

class log_operation:
    """Context Manager für Operation Logging."""
    
    def __init__(self, component: str, operation: str):
        """Initialize log operation context.
        
        Args:
            component: Component/module name for logging
            operation: Operation description
        """
        self.component = component
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start operation timing and logging.
        
        Returns:
            self: Context manager instance
        """
        import time
        self.start_time = time.time()
        log_info(self.component, f"START: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End operation timing and log result.
        
        Args:
            exc_type: Exception type if error occurred
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            log_info(self.component, f"SUCCESS: {self.operation} ({duration:.2f}s)")
        else:
            log_error(self.component, f"FAILED: {self.operation} ({duration:.2f}s)", exc_val)
        
        return False  # Propagate exception


# ──── Example Usage ────────────────────────────────────────────

if __name__ == "__main__":
    logger = get_logger()
    
    logger.debug("TEST", "This is a debug message")
    logger.info("TEST", "This is an info message")
    logger.warning("TEST", "This is a warning message")
    logger.error("TEST", "This is an error message")
    
    # Example: Operation logging
    with log_operation("TEST", "Sample operation"):
        import time
        time.sleep(0.5)
    
    print("\n✅ Logs created in logs/ directory")
