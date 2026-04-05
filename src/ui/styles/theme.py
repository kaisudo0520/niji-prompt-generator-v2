"""
Ink Garden Theme — Niji Prompt Generator
Dark aesthetic: deep ink-blue, warm gold accents, premium atelier feel.
"""

# ─────────────────────────────────────────────
#  Color Palette
# ─────────────────────────────────────────────

class Palette:
    # Backgrounds
    BG_DEEP       = "#0B0B14"
    BG_SURFACE    = "#12121D"
    BG_CARD       = "#191926"
    BG_CARD_HOVER = "#1D1D2E"
    BG_CARD_SEL   = "#1E1A32"
    BG_INPUT      = "#0E0E1A"
    BG_ELEVATED   = "#1E1E2E"

    # Borders
    BORDER        = "#252538"
    BORDER_SUBTLE = "#1C1C2C"
    BORDER_FOCUS  = "#7B74A8"

    # Accent (Gold / Warm)
    ACCENT        = "#C9A96E"
    ACCENT_BRIGHT = "#DDBB7A"
    ACCENT_DIM    = "#7A6540"
    ACCENT_BG     = "#201808"

    # Text
    TEXT          = "#EDE7DC"
    TEXT_SUB      = "#9B96AA"
    TEXT_DIM      = "#55516A"
    TEXT_ACCENT   = "#C9A96E"

    # States
    SUCCESS       = "#6B9E7A"
    ERROR         = "#B06060"

    # Scrollbar
    SCROLL        = "#252538"
    SCROLL_HOVER  = "#353550"


# ─────────────────────────────────────────────
#  Artist accent colors (card selection glow)
# ─────────────────────────────────────────────

ARTIST_COLORS: dict[str, str] = {
    "RURUDO":       "#C4A882",
    "kousaki rui":  "#E8A0C0",
    "Anmi":         "#80C4A0",
    "Lake":         "#A090E0",
    "Liduke":       "#8090B0",
}

# ─────────────────────────────────────────────
#  Color value → hex preview dot
# ─────────────────────────────────────────────

COLOR_PREVIEW_MAP: dict[str, str] = {
    "pink and gold":            "#D4957A",
    "rainbow-colored petals":   "#B090C8",
    "dark gray and light black":"#484858",
    "dark bronze and red":      "#8B4A3A",
    "stark black and white":    "#909090",
    "light bronze and blue":    "#5A8090",
    "dark orange and white":    "#C86020",
    "dark gray and red":        "#784050",
}


# ─────────────────────────────────────────────
#  Main QSS Stylesheet
# ─────────────────────────────────────────────

P = Palette  # shorthand alias


STYLESHEET = f"""
/* ═══════════════════════════════════════════
   Base
═══════════════════════════════════════════ */
QWidget {{
    background-color: {P.BG_DEEP};
    color: {P.TEXT};
    font-family: "Microsoft YaHei UI", "Noto Sans CJK SC", "PingFang SC",
                 "Segoe UI", sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}

QMainWindow {{
    background-color: {P.BG_DEEP};
}}

/* ═══════════════════════════════════════════
   Scrollbars
═══════════════════════════════════════════ */
QScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {P.SCROLL};
    border-radius: 3px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {P.SCROLL_HOVER};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    height: 0;
}}

/* ═══════════════════════════════════════════
   Splitter
═══════════════════════════════════════════ */
QSplitter::handle {{
    background: {P.BORDER_SUBTLE};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:horizontal:hover {{
    background: {P.BORDER};
}}

/* ═══════════════════════════════════════════
   Labels
═══════════════════════════════════════════ */
QLabel {{
    background: transparent;
    color: {P.TEXT};
}}

QLabel#sectionLabel {{
    color: {P.TEXT_SUB};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
}}

QLabel#titleLabel {{
    color: {P.TEXT};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}

QLabel#dimLabel {{
    color: {P.TEXT_DIM};
    font-size: 11px;
}}

QLabel#accentLabel {{
    color: {P.ACCENT};
}}

QLabel#statusModel {{
    color: {P.TEXT_DIM};
    font-size: 11px;
    background: transparent;
    padding: 3px 9px;
    border: 1px solid {P.BORDER};
    border-radius: 4px;
}}

/* ═══════════════════════════════════════════
   Text Inputs
═══════════════════════════════════════════ */
QTextEdit {{
    background-color: {P.BG_INPUT};
    color: {P.TEXT};
    border: 1px solid {P.BORDER};
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13px;
    selection-background-color: {P.ACCENT_DIM};
    selection-color: {P.TEXT};
}}

QTextEdit:focus {{
    border: 1px solid {P.BORDER_FOCUS};
}}

QTextEdit#promptOutput {{
    background-color: {P.BG_SURFACE};
    font-family: "Cascadia Code", "Consolas", "JetBrains Mono", "Courier New", monospace;
    font-size: 12px;
    border: 1px solid {P.BORDER};
    border-radius: 8px;
    padding: 16px;
    color: {P.TEXT};
    line-height: 1.7;
}}

/* ═══════════════════════════════════════════
   ComboBox
═══════════════════════════════════════════ */
QComboBox {{
    background-color: {P.BG_INPUT};
    color: {P.TEXT};
    border: 1px solid {P.BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    font-size: 12px;
    min-width: 120px;
}}

QComboBox:hover {{
    border-color: {P.BORDER_FOCUS};
}}

QComboBox:disabled {{
    color: {P.TEXT_DIM};
    border-color: {P.BORDER_SUBTLE};
    background-color: {P.BG_SURFACE};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {P.BG_ELEVATED};
    color: {P.TEXT};
    border: 1px solid {P.BORDER};
    selection-background-color: {P.ACCENT_BG};
    selection-color: {P.ACCENT};
    padding: 4px;
    outline: none;
}}

/* ═══════════════════════════════════════════
   Buttons — base
═══════════════════════════════════════════ */
QPushButton {{
    background-color: {P.BG_ELEVATED};
    color: {P.TEXT};
    border: 1px solid {P.BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {P.BG_CARD_HOVER};
    border-color: {P.BORDER_FOCUS};
}}

QPushButton:pressed {{
    background-color: {P.BG_CARD};
}}

QPushButton:disabled {{
    color: {P.TEXT_DIM};
    border-color: {P.BORDER_SUBTLE};
    background-color: {P.BG_SURFACE};
}}

/* Generate button — primary CTA */
QPushButton#generateBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {P.ACCENT_DIM}, stop:0.45 {P.ACCENT}, stop:1 {P.ACCENT_DIM});
    color: #160F00;
    border: none;
    border-radius: 10px;
    padding: 14px 28px;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QPushButton#generateBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {P.ACCENT}, stop:0.45 {P.ACCENT_BRIGHT}, stop:1 {P.ACCENT});
}}

QPushButton#generateBtn:disabled {{
    background: {P.BG_ELEVATED};
    color: {P.TEXT_DIM};
    border: 1px solid {P.BORDER};
}}

/* Copy button */
QPushButton#copyBtn {{
    background-color: transparent;
    color: {P.ACCENT};
    border: 1px solid {P.ACCENT_DIM};
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 12px;
    font-weight: 600;
}}

QPushButton#copyBtn:hover {{
    background-color: {P.ACCENT_BG};
    border-color: {P.ACCENT};
}}

QPushButton#copyBtn:disabled {{
    color: {P.TEXT_DIM};
    border-color: {P.BORDER};
}}

QPushButton#copyBtn[copied="true"] {{
    color: {P.SUCCESS};
    border-color: {P.SUCCESS};
    background-color: transparent;
}}

/* Ratio pill buttons */
QPushButton#pill {{
    background-color: {P.BG_CARD};
    color: {P.TEXT_SUB};
    border: 1px solid {P.BORDER};
    border-radius: 6px;
    padding: 6px 13px;
    font-size: 12px;
    font-weight: 500;
    min-width: 46px;
}}

QPushButton#pill:hover {{
    background-color: {P.BG_CARD_HOVER};
    color: {P.TEXT};
    border-color: {P.BORDER_FOCUS};
}}

QPushButton#pill[selected="true"] {{
    background-color: {P.ACCENT_BG};
    color: {P.ACCENT};
    border-color: {P.ACCENT};
    font-weight: 700;
}}

/* ═══════════════════════════════════════════
   Artist Cards (QFrame)
═══════════════════════════════════════════ */
QFrame#artistCard {{
    background-color: {P.BG_CARD};
    border: 1px solid {P.BORDER};
    border-radius: 10px;
}}

QFrame#artistCard:hover {{
    background-color: {P.BG_CARD_HOVER};
    border-color: {P.BORDER_FOCUS};
}}

QFrame#artistCard[selected="true"] {{
    background-color: {P.BG_CARD_SEL};
    border-color: {P.ACCENT};
}}

/* ═══════════════════════════════════════════
   Color Chips (QFrame)
═══════════════════════════════════════════ */
QFrame#colorChip {{
    background-color: {P.BG_CARD};
    border: 1px solid {P.BORDER};
    border-radius: 6px;
}}

QFrame#colorChip:hover {{
    background-color: {P.BG_CARD_HOVER};
    border-color: {P.BORDER_FOCUS};
}}

QFrame#colorChip[selected="true"] {{
    background-color: {P.ACCENT_BG};
    border-color: {P.ACCENT};
}}

QFrame#colorChip[is_empty="true"] {{
    border-style: dashed;
    border-color: {P.BORDER};
    background-color: transparent;
}}

QFrame#colorChip[is_empty="true"][selected="true"] {{
    border-style: dashed;
    border-color: {P.BORDER_FOCUS};
    background-color: transparent;
}}

/* ═══════════════════════════════════════════
   GroupBox (field details)
═══════════════════════════════════════════ */
QGroupBox {{
    background: transparent;
    border: 1px solid {P.BORDER_SUBTLE};
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 4px;
    color: {P.TEXT_DIM};
    font-size: 11px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {P.TEXT_DIM};
    font-size: 11px;
    letter-spacing: 0.8px;
    left: 14px;
}}

/* ═══════════════════════════════════════════
   Header bar / dividers
═══════════════════════════════════════════ */
QFrame#headerBar {{
    background-color: {P.BG_SURFACE};
    border-bottom: 1px solid {P.BORDER_SUBTLE};
    min-height: 52px;
    max-height: 52px;
}}

QWidget#generateFooter {{
    background-color: {P.BG_SURFACE};
}}

QFrame#divider {{
    background-color: {P.BORDER_SUBTLE};
    max-height: 1px;
    min-height: 1px;
}}

/* ═══════════════════════════════════════════
   Template selector chips
═══════════════════════════════════════════ */
QFrame#templateChip {{
    background-color: transparent;
    border: 1px solid {P.BORDER};
    border-radius: 7px;
}}

QFrame#templateChip:hover {{
    background-color: {P.BG_CARD_HOVER};
    border-color: {P.BORDER_FOCUS};
}}

QFrame#templateChip[active="true"] {{
    background-color: {P.ACCENT_BG};
    border-color: {P.ACCENT};
}}
"""
