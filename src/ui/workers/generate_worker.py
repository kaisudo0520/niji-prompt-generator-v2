"""
GenerateWorker — Runs PromptService.generate() in a QThread.
Keeps the UI responsive during LLM API calls (which typically take 1–10 s).
"""
from PySide6.QtCore import QThread, Signal


class GenerateWorker(QThread):
    """
    Usage:
        worker = GenerateWorker(prompt_service, request, parent=self)
        worker.finished.connect(self._on_finished)   # receives GenerateResponse
        worker.error.connect(self._on_error)          # receives error string
        worker.start()
    """

    # PySide6: Signal()  (PyQt6 equivalent: pyqtSignal())
    finished = Signal(object)  # GenerateResponse
    error    = Signal(str)

    def __init__(self, prompt_service, request, parent=None):
        super().__init__(parent)
        self._prompt_service = prompt_service
        self._request = request

    def run(self) -> None:
        try:
            response = self._prompt_service.generate(self._request)
            self.finished.emit(response)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
