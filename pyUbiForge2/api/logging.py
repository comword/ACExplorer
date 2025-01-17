import logging
import sys
import os

log = logging.getLogger("pyUbiForge2")
log_level = logging.DEBUG if "debug" in sys.argv else logging.INFO

log.setLevel(log_level)

_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

os.makedirs("./logs", exist_ok=True)
_log_file = logging.FileHandler("./logs/pyUbiForge2.log", "w")
_log_file.setLevel(log_level)
_log_file.setFormatter(_formatter)
log.addHandler(_log_file)

_log_console = logging.StreamHandler()
_log_console.setLevel(log_level)
_log_console.setFormatter(_formatter)
log.addHandler(_log_console)
