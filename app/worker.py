from PyQt6.QtCore import QThread, pyqtSignal
import subprocess
import time
import os


class CommandWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    stats_signal = pyqtSignal(str)  # For speed + ETA
    finished_signal = pyqtSignal(dict)

    def __init__(self, command, archive_path, total_steps=0):
        super().__init__()
        self.command = command
        self.archive_path = archive_path
        self.total_steps = total_steps
        self._process = None
        self._cancelled = False

    def run(self):
        try:
            self._process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            start_time = time.time()
            last_size = 0
            last_time = start_time
            completed = 0
            dup_count = 0  # track repeated duplicate-key noise

            while True:

                # Stream output
                if self._process.stdout:
                    line = self._process.stdout.readline()
                    if line:
                        clean = line.strip()

                        # Collapse "continuing through error: E11000" spam into a summary
                        if "continuing through error" in clean and "E11000" in clean:
                            dup_count += 1
                            continue  # swallow the raw line

                        # Flush pending dup summary before printing the next real line
                        if dup_count > 0:
                            self.log_signal.emit(
                                f"⚠  {dup_count} duplicate key error(s) skipped "
                                f"— enable 'Drop Existing Collections' to avoid this"
                            )
                            dup_count = 0

                        self.log_signal.emit(clean)

                        if "writing" in clean.lower() or "restoring" in clean.lower():
                            completed += 1
                            if self.total_steps > 0:
                                percent = int((completed / self.total_steps) * 100)
                                self.progress_signal.emit(min(percent, 100))

                # Track archive size change (growth for backup, stable/read for restore)
                if os.path.exists(self.archive_path):
                    current_size = os.path.getsize(self.archive_path)
                    current_time = time.time()

                    delta_size = abs(current_size - last_size)  # abs covers both directions
                    delta_time = current_time - last_time

                    if delta_time > 0 and delta_size > 0:
                        speed = delta_size / delta_time  # bytes/sec
                        speed_mb = speed / (1024 * 1024)

                        if self.total_steps > 0 and completed > 0:
                            pct_done = completed / self.total_steps
                            elapsed = current_time - start_time
                            eta = (elapsed / pct_done) * (1 - pct_done) if pct_done < 1 else 0
                        else:
                            eta = 0

                        eta_display = f"{int(eta)}s" if eta > 0 else "--"
                        self.stats_signal.emit(f"{speed_mb:.2f} MB/s | ETA: {eta_display}")

                    last_size = current_size
                    last_time = current_time

                if self._process.poll() is not None:
                    break

                if self._cancelled:
                    self._process.terminate()
                    break

                time.sleep(0.5)

            self._process.wait()

            # Flush any remaining dup summary after process exits
            if dup_count > 0:
                self.log_signal.emit(
                    f"⚠  {dup_count} duplicate key error(s) skipped "
                    f"— enable 'Drop Existing Collections' to avoid this"
                )

            if self._cancelled:
                self.finished_signal.emit({"success": False, "error": "Cancelled"})
                return

            self.finished_signal.emit({
                "success": self._process.returncode == 0
            })

        except Exception as e:
            self.finished_signal.emit({"success": False, "error": str(e)})

    def cancel(self):
        self._cancelled = True