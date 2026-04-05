"""
Development preview — full UI with mock data, no services or API key required.

Usage:
    python dev_preview.py
"""
import sys
from dataclasses import dataclass, field
from typing import List

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.styles.theme import STYLESHEET


# ─────────────────────────────────────────────────────────────────────────────
#  Minimal mock data structures
#  (mirrors Pydantic models so the UI code sees identical attribute access)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Opt:
    value: str
    label: str
    description: str = ""


@dataclass
class CatGroup:
    label: str
    options: List[Opt] = field(default_factory=list)


@dataclass
class MultiCards:
    type: str = "multi_select_cards"
    id: str = ""
    label: str = ""
    options: List[Opt] = field(default_factory=list)
    max_selections: int = 2


@dataclass
class Pills:
    type: str = "single_select_pills"
    id: str = ""
    label: str = ""
    options: List[Opt] = field(default_factory=list)
    default: str = ""


@dataclass
class CatSelect:
    type: str = "category_select"
    id: str = ""
    label: str = ""
    categories: List[CatGroup] = field(default_factory=list)
    allow_empty: bool = False
    empty_label: str = "讓 LLM 決定"


@dataclass
class FieldDef:
    key: str
    label: str
    hint: str = ""


@dataclass
class Template:
    id: str
    name: str
    description: str
    icon: str = ""
    user_inputs: list = field(default_factory=list)
    fields: list = field(default_factory=list)
    system_prompt: str = ""
    output_template: str = ""
    fixed_suffix: str = ""


# ─────────────────────────────────────────────────────────────────────────────
#  Mock niji-anime template
# ─────────────────────────────────────────────────────────────────────────────

NIJI_TEMPLATE = Template(
    id="niji-anime",
    name="Niji Anime",
    description="生成 Midjourney niji 7 動漫風格提示詞",
    icon="🎨",
    user_inputs=[
        MultiCards(
            id="artists",
            label="參考繪師（1~2 名）",
            max_selections=2,
            options=[
                Opt("RURUDO",       "RURUDO",                  "細膩線條、淡雅色彩、夢幻感"),
                Opt("kousaki rui",  "kousaki rui（光崎琉衣）",   "柔和粉彩、少女感、花卉裝飾"),
                Opt("Anmi",         "Anmi",                    "鮮豔配色、活潑表情、動感構圖"),
                Opt("Lake",         "Lake",                    "精緻珠寶感、光澤質感、華麗服裝"),
                Opt("Liduke",       "Liduke",                  "獨特眼神、神秘氛圍、複雜細節"),
            ],
        ),
        Pills(
            id="aspect_ratio",
            label="圖像比例",
            default="9:16",
            options=[
                Opt("16:9", "16:9"),
                Opt("1:1",  "1:1"),
                Opt("4:3",  "4:3"),
                Opt("3:4",  "3:4"),
                Opt("9:16", "9:16"),
            ],
        ),
        CatSelect(
            id="color_palette",
            label="主色調 / 光芒色彩",
            allow_empty=True,
            empty_label="讓 LLM 決定",
            categories=[
                CatGroup("夢幻 / 華麗", [
                    Opt("pink and gold",          "粉與金"),
                    Opt("rainbow-colored petals", "彩虹色花瓣"),
                ]),
                CatGroup("神祕 / 暗黑", [
                    Opt("dark gray and light black", "深灰與淺黑"),
                    Opt("dark bronze and red",       "深古銅與紅"),
                    Opt("stark black and white",     "強烈的黑白"),
                ]),
                CatGroup("憂鬱 / 氣氛", [
                    Opt("light bronze and blue", "淺古銅與藍"),
                    Opt("dark orange and white", "深橘與白"),
                    Opt("dark gray and red",     "深灰與紅"),
                ]),
            ],
        ),
    ],
    fields=[
        FieldDef("character_and_shot",     "人物與鏡頭",      "e.g. 1girl, upper body"),
        FieldDef("outfit_and_accessories", "服裝與配件"),
        FieldDef("hair_and_eyes",          "髮色與瞳色"),
        FieldDef("expression_and_action",  "表情與動作"),
        FieldDef("color_palette",          "主色調 / 光芒色彩"),
        FieldDef("lighting",               "打光類型"),
        FieldDef("scene_and_atmosphere",   "場景與氛圍"),
        FieldDef("composition",            "構圖修飾"),
    ],
)


# ─────────────────────────────────────────────────────────────────────────────
#  Mock service
# ─────────────────────────────────────────────────────────────────────────────

class MockTemplateService:
    def get_all(self) -> list:
        return [NIJI_TEMPLATE]

    def load(self, template_id: str) -> Template:
        if template_id == "niji-anime":
            return NIJI_TEMPLATE
        raise ValueError(f"Unknown template: {template_id!r}")


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Niji Prompt Generator — Dev Preview")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow(
        template_service=MockTemplateService(),
        prompt_service=None,   # dev mode: returns fixed mock output
        llm_config=None,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
