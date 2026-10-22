import json
import os


class WriteAheadLog:

    def __init__(self, filepath: str = "wal.log"):
        self.filepath = filepath
        # Line-buffered file handle so data hits disk immediately
        self.file = open(self.filepath, "a", buffering=1)

    def log_action(self, action: str, key: str, value: str = None) -> None:
        """Append an entry to the log file."""
        record = json.dumps({"action": action, "key": key, "value": value})
        self.file.write(record + "\n")

    def recover(self, engine) -> None:
        """Replay log commands into the memory engine upon startup."""
        if not os.path.exists(self.filepath):
            return

        with open(self.filepath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if entry["action"] == "SET":
                    engine.set(entry["key"], entry["value"])
                elif entry["action"] == "DELETE":
                    engine.delete(entry["key"])