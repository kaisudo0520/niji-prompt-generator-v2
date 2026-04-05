"""
Production entry point — wires up all services and launches the application.
Requires OPENROUTER_API_KEY in .env or environment.
"""
import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from src.ui.styles.theme import STYLESHEET


_ROOT = Path(__file__).resolve().parent


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Niji Prompt Generator")
    app.setStyleSheet(STYLESHEET)

    # Load .env if present
    try:
        from dotenv import load_dotenv
        load_dotenv(_ROOT / ".env")
    except ImportError:
        pass

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        QMessageBox.critical(
            None,
            "缺少 API Key",
            "請在 .env 檔案中設定 OPENROUTER_API_KEY。\n\n"
            "複製 .env.example 為 .env 並填入您的 OpenRouter API Key。",
        )
        sys.exit(1)

    try:
        from src.services.template_service import TemplateService
        from src.services.llm_service import LLMService
        from src.services.prompt_service import PromptService
        from src.config.llm_config_loader import load_llm_config

        llm_config       = load_llm_config(_ROOT / "config" / "llm_config.json")
        template_service = TemplateService(_ROOT / "templates")
        llm_service      = LLMService(llm_config, api_key)
        prompt_service   = PromptService(template_service, llm_service)

    except Exception as exc:
        QMessageBox.critical(None, "初始化失敗", str(exc))
        sys.exit(1)

    from src.ui.main_window import MainWindow
    window = MainWindow(
        template_service=template_service,
        prompt_service=prompt_service,
        llm_config=llm_config,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
