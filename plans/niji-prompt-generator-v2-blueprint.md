# Blueprint — Niji Prompt Generator v2

**Objective:** 建立可擴充的桌面應用程式，讓使用者輸入描述，透過 LLM 自動補全欄位後輸出 Midjourney 提示詞，並一鍵複製。採用**可插拔 JSON 模板架構**，初版實作 `niji-anime` 模板，模型與模板均可由設定檔動態切換。

**Date:** 2026-04-05
**Status:** Draft
**Mode:** Desktop Application (Python + PySide6)

---

## 0. 技術棧決策與建議

### 0.1 確認採用

| 層級 | 選用 | 說明 |
|------|------|------|
| GUI | **PySide6** | 跨平台桌面 UI，Qt Company 官方 Python 綁定，LGPL 授權 |
| 語言 | **Python 3.11+** | |
| LLM 路由 | **OpenRouter** | 統一 API 入口，支援多家模型 |
| 模型 | `google/gemini-flash-1.5-preview` | 可透過 JSON 設定切換 |
| 模板存放 | **JSON 檔案** | 無需資料庫，易於手動編輯與版控 |
| 測試 | **pytest** | TDD 主力 |

### 0.2 建議調整（供參考）

#### 建議：Phase 1 不引入 FastAPI
FastAPI 的價值在於：多使用者/多裝置存取、HTTP 介面供其他程式呼叫。  
桌面單人應用不需要，且會增加啟動複雜度（需跑 uvicorn server）。

**建議架構：**
```
PySide6 UI → Service Layer (純 Python) → OpenRouter HTTP
```
Service Layer 完全不依賴 UI，可獨立 pytest 測試。  
未來若需要 Web 版本，直接將 Service Layer 包成 FastAPI router，**零重構**。

> **本 blueprint 採用此架構，FastAPI 作為未來擴充項列入 §11。**

#### 建議 3：模型 ID 確認
`google/gemini-3-flash-preview` 請在 [openrouter.ai/models](https://openrouter.ai/models) 確認目前有效 ID，並填入 `config/llm_config.json`。  
本 blueprint 以 `google/gemini-2.5-flash-preview` 作為示例佔位符。

---

## 1. 專案概覽

### 1.1 核心原則：模板即 JSON，行為即 Service

```
[JSON Template]  ─→  TemplateService.load()  ─→  TemplateDefinition (Pydantic)
[llm_config.json] ─→  LLMService            ─→  OpenRouter API
                                ↓
                       PromptService.generate()
                                ↓
                         PySide6 UI 顯示
```

### 1.2 使用者流程

```
啟動 App → 自動載入所有 JSON 模板
      ↓
選擇模板（初版 1 個，UI 保留位置）
      ↓
UI 根據模板動態渲染表單（選繪師、比例、色調等）
      ↓
輸入描述 → 點擊「生成」
      ↓
Worker Thread: PromptService → LLM → buildPrompt
      ↓
顯示完整 prompt + 一鍵複製
```

---

## 2. 目錄結構

```
niji-prompt-generator-v2/
│
├── src/
│   ├── ui/                            # PySide6 UI 層（只負責顯示與事件）
│   │   ├── main_window.py             # QMainWindow：頂層佈局
│   │   ├── widgets/
│   │   │   ├── template_selector.py   # 模板選擇卡片列表
│   │   │   ├── dynamic_form.py        # 根據模板定義動態渲染表單
│   │   │   ├── prompt_output.py       # 輸出區塊 + 複製按鈕
│   │   │   └── inputs/                # 可複用輸入元件（模板無關）
│   │   │       ├── multi_select_cards.py
│   │   │       ├── single_select_pills.py
│   │   │       └── category_select.py
│   │   └── workers/
│   │       └── generate_worker.py     # QThread：非同步 LLM 呼叫
│   │
│   ├── services/                      # 業務邏輯層（無 UI 依賴，可獨立測試）
│   │   ├── template_service.py        # 讀取並驗證 JSON 模板
│   │   ├── llm_service.py             # OpenRouter API 呼叫
│   │   └── prompt_service.py          # 協調：模板 → LLM → buildPrompt
│   │
│   └── models/                        # Pydantic 資料模型（即規格文件）
│       ├── template.py                # TemplateDefinition, FieldDef, UserInputDef
│       ├── llm_config.py              # LLMConfig, ModelOption
│       └── api.py                     # GenerateRequest, GenerateResponse
│
├── templates/                         # JSON 模板檔案（可新增，無需改程式碼）
│   └── niji-anime.json
│
├── config/
│   └── llm_config.json                # 模型路由設定（可熱切換）
│
├── tests/                             # TDD 測試（與 src/ 鏡像結構）
│   ├── services/
│   │   ├── test_template_service.py
│   │   ├── test_llm_service.py
│   │   └── test_prompt_service.py
│   ├── models/
│   │   └── test_template_models.py
│   └── conftest.py                    # pytest fixtures
│
├── .env                               # OPENROUTER_API_KEY（不提交）
├── .env.example
├── requirements.txt
├── requirements-dev.txt               # pytest, pytest-qt, pytest-mock
├── plan.md
└── main.py                            # 進入點：QApplication（PySide6）+ MainWindow
```

---

## 3. 資料模型規格（Pydantic = SDD 規格文件）

> **SDD 原則：** Pydantic model 既是型別定義，也是 JSON 驗證 schema，也是測試的規格基準。先定義 model，再寫服務，再寫 UI。

### 3.1 `src/models/template.py`

```python
from __future__ import annotations
from typing import Literal, Union
from pydantic import BaseModel, Field


class SelectOption(BaseModel):
    value: str
    label: str           # 中文顯示
    description: str = ""  # 特色標註（如繪師風格）


class MultiSelectCardsInput(BaseModel):
    type: Literal["multi_select_cards"]
    id: str
    label: str
    options: list[SelectOption]
    max_selections: int = Field(ge=1)


class SingleSelectPillsInput(BaseModel):
    type: Literal["single_select_pills"]
    id: str
    label: str
    options: list[SelectOption]
    default: str = ""


class CategorySelectInput(BaseModel):
    type: Literal["category_select"]
    id: str
    label: str
    categories: list[CategoryGroup]
    allow_empty: bool = False
    empty_label: str = "讓 LLM 決定"


class CategoryGroup(BaseModel):
    label: str
    options: list[SelectOption]


UserInputDef = Union[MultiSelectCardsInput, SingleSelectPillsInput, CategorySelectInput]


class FieldDef(BaseModel):
    key: str
    label: str    # 中文欄位名
    hint: str = ""


class TemplateDefinition(BaseModel):
    id: str
    name: str
    description: str
    icon: str = ""
    user_inputs: list[UserInputDef] = Field(discriminator="type")
    fields: list[FieldDef]
    system_prompt: str
    # Jinja2-like 模板字串，LLM 填寫的欄位用 {key} 表示，使用者輸入用 {input.key}
    output_template: str
    fixed_suffix: str = ""
```

### 3.2 `src/models/llm_config.py`

```python
from pydantic import BaseModel


class ModelOption(BaseModel):
    id: str           # OpenRouter model ID, e.g. "google/gemini-2.5-flash-preview"
    name: str         # 顯示名稱


class LLMConfig(BaseModel):
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    active_model: str
    available_models: list[ModelOption]
    temperature: float = 0.7
    max_tokens: int = 1024
```

### 3.3 `src/models/api.py`

```python
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    template_id: str
    user_description: str
    user_inputs: dict[str, object]  # key = UserInputDef.id, value = 使用者選擇


class GenerateResponse(BaseModel):
    prompt: str                      # 最終 Midjourney 字串
    fields: dict[str, str]           # LLM 填寫的各欄位
    template_id: str
```

---

## 4. JSON 檔案格式

### 4.1 `templates/niji-anime.json`

```json
{
  "id": "niji-anime",
  "name": "Niji Anime",
  "description": "生成 Midjourney niji 7 動漫風格提示詞，支援繪師風格參考",
  "icon": "🎨",
  "user_inputs": [
    {
      "type": "multi_select_cards",
      "id": "artists",
      "label": "參考繪師（1~2 名）",
      "max_selections": 2,
      "options": [
        { "value": "RURUDO",       "label": "RURUDO",              "description": "細膩線條、淡雅色彩、夢幻感" },
        { "value": "kousaki rui",  "label": "kousaki rui（光崎琉衣）", "description": "柔和粉彩、少女感、花卉裝飾" },
        { "value": "Anmi",         "label": "Anmi",                "description": "鮮豔配色、活潑表情、動感構圖" },
        { "value": "Lake",         "label": "Lake",                "description": "精緻珠寶感、光澤質感、華麗服裝" },
        { "value": "Liduke",       "label": "Liduke",              "description": "獨特眼神、神秘氛圍、複雜細節" }
      ]
    },
    {
      "type": "single_select_pills",
      "id": "aspect_ratio",
      "label": "圖像比例",
      "default": "9:16",
      "options": [
        { "value": "16:9", "label": "16:9" },
        { "value": "1:1",  "label": "1:1"  },
        { "value": "4:3",  "label": "4:3"  },
        { "value": "3:4",  "label": "3:4"  },
        { "value": "9:16", "label": "9:16" }
      ]
    },
    {
      "type": "category_select",
      "id": "color_palette",
      "label": "主色調 / 光芒色彩",
      "allow_empty": true,
      "empty_label": "讓 LLM 決定",
      "categories": [
        {
          "label": "夢幻 / 華麗",
          "options": [
            { "value": "pink and gold",          "label": "粉與金" },
            { "value": "rainbow-colored petals", "label": "彩虹色花瓣" }
          ]
        },
        {
          "label": "神祕 / 暗黑",
          "options": [
            { "value": "dark gray and light black", "label": "深灰與淺黑" },
            { "value": "dark bronze and red",       "label": "深古銅與紅" },
            { "value": "stark black and white",     "label": "強烈的黑白" }
          ]
        },
        {
          "label": "憂鬱 / 氣氛",
          "options": [
            { "value": "light bronze and blue", "label": "淺古銅與藍" },
            { "value": "dark orange and white", "label": "深橘與白"   },
            { "value": "dark gray and red",     "label": "深灰與紅"   }
          ]
        }
      ]
    }
  ],
  "fields": [
    { "key": "character_and_shot",     "label": "人物與鏡頭",      "hint": "e.g. 1girl, upper body, looking at viewer" },
    { "key": "outfit_and_accessories", "label": "服裝與配件" },
    { "key": "hair_and_eyes",          "label": "髮色與瞳色" },
    { "key": "expression_and_action",  "label": "表情與動作" },
    { "key": "color_palette",          "label": "主色調 / 光芒色彩" },
    { "key": "lighting",               "label": "打光類型" },
    { "key": "scene_and_atmosphere",   "label": "場景與氛圍" },
    { "key": "composition",            "label": "構圖修飾" }
  ],
  "system_prompt": "You are an expert Midjourney prompt engineer specializing in anime (niji) style.\nExpand the user's brief description into specific, vivid English prompt segments.\nEach segment must be concrete and visual — avoid vague mood words.\nOutput ONLY valid JSON with the exact keys listed, no other text.",
  "output_template": "{character_and_shot}, {outfit_and_accessories}, {hair_and_eyes}, {expression_and_action}, {color_palette}, {lighting}, luminous brushwork, use of light and shadow, {scene_and_atmosphere}, {artist_ref}, official art, anime aesthetic, {composition}",
  "fixed_suffix": "--ar {aspect_ratio} --niji 7 --s 750"
}
```

> `output_template` 中 `{key}` 對應 LLM 欄位，`{artist_ref}` 和 `{aspect_ratio}` 是 PromptService 特殊處理的使用者輸入。

### 4.2 `config/llm_config.json`

```json
{
  "provider": "openrouter",
  "base_url": "https://openrouter.ai/api/v1",
  "active_model": "google/gemini-2.5-flash-preview",
  "temperature": 0.7,
  "max_tokens": 1024,
  "available_models": [
    { "id": "google/gemini-2.5-flash-preview", "name": "Gemini 2.5 Flash (預設)" },
    { "id": "google/gemini-flash-1.5",         "name": "Gemini 1.5 Flash" },
    { "id": "anthropic/claude-3.5-haiku",      "name": "Claude 3.5 Haiku" },
    { "id": "openai/gpt-4o-mini",              "name": "GPT-4o Mini" }
  ]
}
```

---

## 5. Service Layer 設計

### 5.1 `TemplateService`（`src/services/template_service.py`）

```python
class TemplateService:
    def load_all(self, templates_dir: Path) -> list[TemplateDefinition]
    def load(self, template_id: str) -> TemplateDefinition
    def get_registered_ids(self) -> list[str]
```

- 啟動時掃描 `templates/` 目錄，解析所有 `.json` → Pydantic 驗證
- 驗證失敗的模板：記錄 warning，跳過，不崩潰
- 提供 `load(id)` 供其他 service 使用

### 5.2 `LLMService`（`src/services/llm_service.py`）

```python
class LLMService:
    def __init__(self, config: LLMConfig, api_key: str)
    def complete(self, system_prompt: str, user_message: str) -> str
    # 回傳 LLM 原始文字（呼叫方負責 JSON parse）
```

- 使用 `httpx` 呼叫 OpenRouter `/chat/completions`
- 單一職責：只負責 HTTP 通訊，不解析業務邏輯
- 拋出自訂 `LLMError`（含 status_code, message）

### 5.3 `PromptService`（`src/services/prompt_service.py`）

```python
class PromptService:
    def __init__(self, template_service: TemplateService, llm_service: LLMService)
    def generate(self, request: GenerateRequest) -> GenerateResponse
```

核心流程：
```
1. template_service.load(request.template_id)
2. build_user_message(template, request)  ← 組裝 LLM 的 user message
3. llm_service.complete(template.system_prompt, user_message)
4. json.loads(llm_response)  ← 解析 LLM JSON
5. validate_fields(template.fields, llm_fields)  ← 確認所有欄位存在
6. build_prompt(template, llm_fields, request.user_inputs)  ← 組裝最終字串
7. return GenerateResponse(...)
```

**`build_prompt` 邏輯：**
- 以 `output_template` 為基礎，替換 `{field_key}` → LLM 填寫值
- 特殊處理 `{artist_ref}`：1 名 → `in the style of X`，2 名 → `in the style of X and Y`
- 附加 `fixed_suffix`，替換 `{aspect_ratio}` 等使用者輸入佔位符

---

## 6. PySide6 UI 設計

### 6.1 佈局

```
QMainWindow
└── QWidget (central)
    ├── TemplateSelector (QWidget, 初版可摺疊)
    └── QSplitter (vertical)
        ├── DynamicForm (QScrollArea)
        │   ├── QTextEdit (使用者描述)
        │   ├── [動態渲染的 UserInput 元件 × N]
        │   └── QPushButton "生成提示詞"
        └── PromptOutput (QWidget)
            ├── QTextEdit (readonly, monospace)
            ├── QPushButton "複製"
            └── QGroupBox "欄位明細" (collapsible)
```

### 6.2 動態表單渲染（`DynamicForm`）

```python
def render_template(self, template: TemplateDefinition) -> None:
    self._clear_inputs()
    for input_def in template.user_inputs:
        widget = self._create_input_widget(input_def)
        self._layout.addWidget(widget)

def _create_input_widget(self, input_def: UserInputDef) -> QWidget:
    match input_def.type:
        case "multi_select_cards":  return MultiSelectCards(input_def)
        case "single_select_pills": return SingleSelectPills(input_def)
        case "category_select":     return CategorySelect(input_def)
```

> 新增模板不需新寫 UI 元件，除非用到新的 `type`。

### 6.3 Worker Thread（非同步 LLM 呼叫）

PySide6 使用 `Signal`（非 PyQt6 的 `pyqtSignal`），從 `PySide6.QtCore` import：

```python
from PySide6.QtCore import QThread, Signal

class GenerateWorker(QThread):
    # PySide6: Signal()，PyQt6 則為 pyqtSignal()
    finished = Signal(object)   # 傳遞 GenerateResponse
    error    = Signal(str)

    def __init__(self, prompt_service, request, parent=None):
        super().__init__(parent)
        self.prompt_service = prompt_service
        self.request = request

    def run(self):
        try:
            response = self.prompt_service.generate(self.request)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))
```

> **PySide6 vs PyQt6 主要差異（本專案相關）：**
> | | PySide6 | PyQt6 |
> |---|---|---|
> | Signal | `from PySide6.QtCore import Signal` | `from PyQt6.QtCore import pyqtSignal` |
> | Slot | `from PySide6.QtCore import Slot` | `from PyQt6.QtCore import pyqtSlot` |
> | App 啟動 | `app.exec()` | `app.exec()` （兩者相同）|
> | Enum 存取 | `Qt.AlignLeft` 或 `Qt.AlignmentFlag.AlignLeft` | 必須完整路徑 |

UI 點擊「生成」後：
1. 按鈕 disabled + 顯示 spinner
2. 啟動 `GenerateWorker`
3. `finished` signal → 更新輸出區塊、按鈕恢復
4. `error` signal → 顯示錯誤對話框

---

## 7. TDD 測試規格

### 7.1 測試原則

| 原則 | 說明 |
|------|------|
| 先寫測試 | 每個 service 方法先寫 `test_` 再實作 |
| 服務層獨立測試 | 不啟動 PySide6，不呼叫真實 LLM |
| Mock LLM | `pytest-mock` mock `LLMService.complete()` |
| 固定測試資料 | `tests/fixtures/` 存放測試用 JSON 模板與 LLM 回應 |
| 覆蓋率目標 | Service layer ≥ 80%，UI layer 手動測試 |

### 7.2 測試案例清單（`tests/services/test_prompt_service.py`）

```python
# 正常流程
def test_generate_returns_complete_prompt()
def test_generate_uses_user_selected_color_palette()
def test_generate_llm_decides_color_palette_when_empty()
def test_generate_single_artist_style_ref()
def test_generate_two_artist_style_ref()
def test_prompt_ends_with_niji_suffix()

# 邊界條件
def test_generate_raises_when_template_not_found()
def test_generate_raises_when_llm_returns_invalid_json()
def test_generate_raises_when_llm_fields_incomplete()

# 整合（可選，標記 @pytest.mark.integration，CI 預設跳過）
def test_generate_real_llm_call()
```

### 7.3 測試案例清單（`tests/services/test_template_service.py`）

```python
def test_load_all_returns_valid_templates()
def test_load_by_id_returns_correct_template()
def test_load_skips_invalid_json_with_warning()
def test_load_raises_when_id_not_found()
def test_user_inputs_discriminator_resolves_correct_type()
```

---

## 8. 實作步驟（依序執行）

---

### Step 1 — 環境與專案骨架

**Context brief:** 建立 Python 虛擬環境、安裝依賴、建立目錄結構。

**Task list:**
- [ ] `python -m venv .venv && source .venv/Scripts/activate`
- [ ] `requirements.txt`：`PySide6`, `pydantic`, `httpx`, `python-dotenv`
- [ ] `requirements-dev.txt`：`pytest`, `pytest-qt`, `pytest-mock`, `pytest-cov`
  > `pytest-qt` 同時支援 PyQt6 和 PySide6，無需額外設定
- [ ] `pip install -r requirements.txt -r requirements-dev.txt`
- [ ] 建立目錄：`src/ui/widgets/inputs/`, `src/services/`, `src/models/`, `src/ui/workers/`, `tests/services/`, `tests/models/`, `config/`, `templates/`
- [ ] 建立 `.env.example`（`OPENROUTER_API_KEY=`）與 `.gitignore`（含 `.env`, `__pycache__`, `.venv`）
- [ ] 建立空的 `__init__.py` 於各 `src/` 子目錄

**Verification:**
```bash
python -c "import PySide6; import pydantic; import httpx; print('OK')"
pytest --collect-only  # 應顯示 0 tests collected（尚無測試）
```

---

### Step 2 — Pydantic 模型（規格先行）

**Context brief:** 定義所有資料模型。這是 SDD 的核心——模型即規格，後續所有實作以此為準。

**Task list:**
- [ ] `src/models/template.py`（依 §3.1）
- [ ] `src/models/llm_config.py`（依 §3.2）
- [ ] `src/models/api.py`（依 §3.3）
- [ ] `tests/models/test_template_models.py`：測試 `UserInputDef` discriminator 正確解析 3 種 type

**Verification:**
```bash
pytest tests/models/ -v
npx tsc --noEmit  # N/A, 改為：
python -c "from src.models.template import TemplateDefinition; print('models OK')"
```
**Exit criteria:** 模型可 import，discriminator 測試通過。

---

### Step 3 — JSON 模板與設定檔

**Context brief:** 建立 `templates/niji-anime.json` 與 `config/llm_config.json`，並確保 Pydantic 能驗證它們。

**Task list:**
- [ ] `templates/niji-anime.json`（依 §4.1）
- [ ] `config/llm_config.json`（依 §4.2，填入正確的 gemini model ID）
- [ ] `tests/fixtures/niji_anime_template.json`（測試用，可與生產版相同）
- [ ] `tests/fixtures/mock_llm_response.json`：模擬 LLM 回傳的 JSON

**Verification:**
```python
# 手動驗證
from src.models.template import TemplateDefinition
import json
t = TemplateDefinition(**json.loads(open('templates/niji-anime.json').read()))
print(t.id, len(t.user_inputs), len(t.fields))
```
**Exit criteria:** JSON 可正確解析為 Pydantic model，無驗證錯誤。

---

### Step 4 — TemplateService（TDD）

**Context brief:** 先寫測試，再實作 `TemplateService`。

**Task list:**
- [ ] `tests/services/test_template_service.py`（依 §7.3 測試清單）
- [ ] 執行測試 → 全部 FAIL（預期）
- [ ] 實作 `src/services/template_service.py`
- [ ] 執行測試 → 全部 PASS

**Verification:**
```bash
pytest tests/services/test_template_service.py -v --tb=short
```
**Exit criteria:** 所有 template service 測試通過。

---

### Step 5 — LLMService（TDD）

**Context brief:** 實作 OpenRouter HTTP 客戶端，測試使用 `httpx` mock。

**Task list:**
- [ ] `tests/services/test_llm_service.py`：
  - `test_complete_sends_correct_headers()`（驗證 Authorization header）
  - `test_complete_returns_content_from_response()`
  - `test_complete_raises_llm_error_on_4xx()`
  - `test_complete_raises_llm_error_on_rate_limit()`
- [ ] 執行測試 → FAIL
- [ ] 實作 `src/services/llm_service.py`
- [ ] 執行測試 → PASS
- [ ] `src/config/llm_config_loader.py`：從 `config/llm_config.json` + `.env` 讀取設定

**Verification:**
```bash
pytest tests/services/test_llm_service.py -v
```

---

### Step 6 — PromptService（TDD）

**Context brief:** 先寫測試，再實作核心業務邏輯。Mock LLMService。

**Task list:**
- [ ] `tests/services/test_prompt_service.py`（依 §7.2 測試清單）
- [ ] 執行測試 → FAIL
- [ ] 實作 `src/services/prompt_service.py`（依 §5.3 流程）
- [ ] 執行測試 → PASS

**Verification:**
```bash
pytest tests/services/ -v --cov=src/services --cov-report=term-missing
# 目標：coverage ≥ 80%
```
**Exit criteria:** 所有 service 測試通過，覆蓋率 ≥ 80%。

---

### Step 7 — PyQt6 UI 元件

**Context brief:** 實作 3 種輸入元件（模板無關）、DynamicForm、PromptOutput。前端先行，使用假資料測試渲染。

**Task list:**
- [ ] `src/ui/widgets/inputs/multi_select_cards.py`：卡片網格，超過 max 時其他卡片 disabled
- [ ] `src/ui/widgets/inputs/single_select_pills.py`：橫排 pill 按鈕群組，互斥單選
- [ ] `src/ui/widgets/inputs/category_select.py`：分類 + 空值選項
- [ ] `src/ui/widgets/dynamic_form.py`：`render_template()` → match-case 創建對應元件
- [ ] `src/ui/widgets/prompt_output.py`：readonly QTextEdit + 複製按鈕 + 欄位明細（QGroupBox collapsible）
- [ ] `src/ui/workers/generate_worker.py`：`QThread` + `Signal`（依 §6.3，注意 PySide6 用 `Signal` 非 `pyqtSignal`）
- [ ] 建立 `dev_preview.py`：載入 niji-anime 模板，直接顯示 DynamicForm，供視覺開發用

**Verification:**
```bash
python dev_preview.py  # 手動驗證 UI 渲染，不需 LLM
```
**Exit criteria:** 3 種輸入元件渲染正確，選擇狀態有視覺回饋，MultiSelectCards 超過上限攔截。

---

### Step 8 — 主視窗整合

**Context brief:** 整合所有元件，完成完整使用者流程。

**Task list:**
- [ ] `src/ui/main_window.py`：佈局（依 §6.1），連接 DynamicForm → GenerateWorker → PromptOutput
- [ ] `main.py`：初始化 `QApplication`、依賴注入（TemplateService, LLMService, PromptService）、啟動主視窗
- [ ] `src/ui/widgets/template_selector.py`：顯示已注冊模板清單（初版 1 個模板也渲染，保留位置）
- [ ] 錯誤處理：`error` signal → `QMessageBox.critical()`

**Verification:**
1. 啟動 `python main.py`
2. 輸入「銀髮魔法少女」+ 選 RURUDO + 9:16
3. 點擊生成 → 確認 prompt 結尾 `--niji 7 --s 750`
4. 點擊複製 → 確認剪貼簿

**Exit criteria:** 完整流程跑通。

---

### Step 9 — 樣式打磨

**Task list:**
- [ ] 套用 QSS（Qt Style Sheet）：深色主題或淡雅日系風格
- [ ] 繪師卡片：固定寬度、圖示區、名稱加粗、描述小字灰色
- [ ] 輸出區塊：等寬字體（Consolas / Courier New）、淺色背景
- [ ] Loading 狀態：按鈕文字改為「生成中…」+ 禁用
- [ ] 最小視窗尺寸：`setMinimumSize(700, 500)`
- [ ] 視窗標題：「Niji Prompt Generator」

---

## 9. 步驟依賴關係

```
Step 1 (環境)
    ↓
Step 2 (Pydantic 模型)
    ↓
Step 3 (JSON 檔案)
    ↓
Step 4 (TemplateService) ─────────────────────────────┐
    ↓                                                  │
Step 5 (LLMService) ──────────────────────────────────┤
    ↓                                                  │
Step 6 (PromptService)        Step 7 (UI 元件) ←───────┘
    ↓                             ↓
    └──────────────┬──────────────┘
                   ↓
             Step 8 (整合)
                   ↓
             Step 9 (樣式)
```

Steps 6 和 7 可**平行開發**（Step 3 完成後互不依賴），在 Step 8 整合。

---

## 10. 關鍵設計決策

### 10.1 為何 JSON 模板而非 Python 程式碼模板？
- 非開發者也能新增/修改模板（只需編輯 JSON）
- 版控清晰（模板資料變更 vs 邏輯變更分離）
- 未來可做「模板編輯器」UI 直接讀寫 JSON
- Pydantic 提供免費的 JSON schema 驗證

### 10.2 為何 `output_template` 用字串佔位符而非 Python 函式？
Python 函式無法序列化為 JSON。字串佔位符模式（`{key}`）足夠表達所有已知模板的組裝需求，特殊欄位（`{artist_ref}`）由 `PromptService` 預處理。若未來遇到複雜邏輯，可在 `PromptService` 以 template_id 做特殊分支，而不影響 JSON 結構。

### 10.3 為何不引入 FastAPI？
桌面單人應用不需要 HTTP server。Service Layer 已完全解耦，未來包成 FastAPI 只需加 `@app.post("/generate")` wrapper，**零重構服務邏輯**。

### 10.4 Worker Thread 的必要性
PyQt6 主執行緒（UI thread）阻塞 > 100ms 就會出現卡頓/無回應。LLM 呼叫通常 1~10 秒，必須在 `QThread` 執行。

### 10.5 依賴注入而非 Singleton
`main.py` 建立 services 實例後注入 `MainWindow`，避免全域狀態，讓測試可輕易替換 mock。

---

## 11. 錯誤處理策略

| 情境 | 服務層行為 | UI 行為 |
|------|----------|--------|
| API Key 未設定 | `LLMService.__init__` 拋出 `ValueError` | 啟動時 `QMessageBox.critical` 後退出 |
| 模板 JSON 格式錯誤 | `TemplateService` 跳過並 warning | 模板不出現在選單 |
| LLM 回傳非 JSON | `PromptService` 拋出 `LLMParseError` | error signal → 對話框 |
| LLM 欄位不完整 | `PromptService` 拋出 `FieldMissingError` | error signal → 對話框 |
| HTTP 4xx/5xx | `LLMService` 拋出 `LLMError(status_code)` | error signal → 對話框，429 顯示「請稍後再試」 |
| 使用者未選繪師 | — | Submit 按鈕 disabled（前端驗證） |

---

## 12. 未來擴充方向

**模板擴充：**
- [ ] `stable-diffusion.json`（不同欄位組合、不同 suffix 格式）
- [ ] `dall-e-3.json`（自然語言描述風格）

**功能擴充：**
- [ ] 模板編輯器：Qt UI 直接讀寫 `templates/*.json`
- [ ] 歷史記錄：SQLite 儲存最近 N 筆 prompt
- [ ] 模型切換 UI：在主視窗 StatusBar 顯示/切換 active_model
- [ ] FastAPI wrapper：Service Layer 包成 REST API，供 Web 版或其他工具呼叫

---

## 13. 驗收標準

- [ ] 輸入「紫髮神官少女，手持法杖」+ Lake + 9:16 → prompt 含 `in the style of Lake`
- [ ] 選色調「dark bronze and red」→ prompt 含該色調
- [ ] 不選色調 → LLM 自動選，prompt 含色調描述
- [ ] 複製按鈕 → 剪貼簿含完整 prompt
- [ ] prompt 結尾固定為 `--niji 7 --s 750`
- [ ] LLM 呼叫中 UI 不卡頓，按鈕顯示「生成中…」
- [ ] `pytest tests/ -v` 全部通過
- [ ] Service layer 測試覆蓋率 ≥ 80%
- [ ] 新增第二個模板只需新增 `templates/<id>.json`，無需改動 Python 程式碼
