"""
GenerateWorker — Runs PromptService.generate() in a QThread.
Keeps the UI responsive during LLM API calls (which typically take 1–10 s).
"""
from PySide6.QtCore import QThread, Signal


class GenerateWorker(QThread):
    """
    Usage:
        worker = GenerateWorker(prompt_service, request, parent=self)
        worker.result_ready.connect(self._on_finished)  # receives GenerateResponse
        worker.error.connect(self._on_error)             # receives error string
        worker.start()

    Note: We use ``result_ready`` instead of ``finished`` to avoid shadowing
    the built-in ``QThread.finished`` signal which fires when the thread exits.
    """

    result_ready = Signal(object)  # GenerateResponse
    error        = Signal(str)

    def __init__(self, prompt_service, request, parent=None):
        super().__init__(parent)
        self._prompt_service = prompt_service
        self._request = request

    def run(self) -> None:
        try:
            response = self._prompt_service.generate(self._request)
            self.result_ready.emit(response)
        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))
