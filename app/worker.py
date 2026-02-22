from PyQt6.QtCore import QThread, pyqtSignal
import subprocess

class CommandWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                self.log_signal.emit(line.strip())

            process.wait()
            self.finished_signal.emit(process.returncode == 0)

        except Exception as e:
            self.log_signal.emit(str(e))
            self.finished_signal.emit(False)
