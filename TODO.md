# TODO — Niji Prompt Generator v2

> 狀態標記：`[ ]` 待做　`[x]` 完成　`[-]` 略過/不做

---

## Phase 1 — 前端 & 核心（已完成）

### Blueprint Step 1：環境與骨架
- [x] Python 3.10 venv（3.12 與 PySide6 在此系統有 DLL 相容問題）
- [x] `requirements.txt`（PySide6, pydantic, httpx, python-dotenv）
- [x] `requirements-dev.txt`（pytest, pytest-mock, pytest-cov）
- [x] 目錄結構建立（src/ui/, src/services/, src/models/, tests/）
- [x] `.env.example`、`.gitignore`

### Blueprint Step 2：Pydantic 模型（SDD 規格）
- [x] `src/models/template.py`（TemplateDefinition, UserInputDef discriminated union）
- [x] `src/models/llm_config.py`（LLMConfig, ModelOption）
- [x] `src/models/api.py`（GenerateRequest, GenerateResponse）

### Blueprint Step 3：JSON 設定檔
- [x] `templates/niji-anime.json`
- [x] `config/llm_config.json`（model: `google/gemini-3-flash-preview`）

### Blueprint Step 4：TemplateService（TDD）
- [x] `src/services/template_service.py`（97% 覆蓋率）
- [x] `tests/services/test_template_service.py`（6 tests）

### Blueprint Step 5：LLMService
- [x] `src/services/llm_service.py`（OpenRouter, httpx）
- [ ] `tests/services/test_llm_service.py`（待補，需 httpx mock）

### Blueprint Step 6：PromptService（TDD）
- [x] `src/services/prompt_service.py`（98% 覆蓋率）
- [x] `tests/services/test_prompt_service.py`（12 tests）

### Blueprint Step 7：PySide6 UI 元件（前端先行）
- [x] `src/ui/styles/theme.py`（Ink Garden 深色主題 QSS）
- [x] `src/ui/widgets/inputs/multi_select_cards.py`（繪師卡片，最多 2 名）
- [x] `src/ui/widgets/inputs/single_select_pills.py`（比例 Pill 按鈕）
- [x] `src/ui/widgets/inputs/category_select.py`（分類色調，含色碼小點）
- [x] `src/ui/widgets/dynamic_form.py`（模板驅動動態表單 + 載入動畫）
- [x] `src/ui/widgets/prompt_output.py`（輸出 + 複製 + 欄位明細摺疊）
- [x] `src/ui/widgets/template_selector.py`（單模板時自動隱藏）
- [x] `src/ui/workers/generate_worker.py`（QThread，非同步 LLM 呼叫）

### Blueprint Step 8：主視窗整合
- [x] `src/ui/main_window.py`
- [x] `dev_preview.py`（Mock 資料，無需 API Key）
- [x] `main.py`（生產進入點）

---

## Phase 2 — 待完成

### 測試補齊
- [x] `tests/services/test_llm_service.py`（82% 覆蓋率，5 tests）
  - `test_complete_sends_correct_authorization_header()`
  - `test_complete_returns_content_from_response()`
  - `test_complete_raises_on_401()`
  - `test_complete_raises_on_429_with_friendly_message()`
  - `test_complete_raises_on_timeout()`

### 樣式打磨（Blueprint Step 9）
- [x] 驗證 dev_preview 視窗在 1080p / 1440p 螢幕的排版（三行佈局 + 下拉式比例/色調）
- [x] 繪師卡片選中後邊框使用對應 ARTIST_COLORS 顏色（inline setStyleSheet 覆寫）
- [x] Loading 時 Generate 按鈕加入 QPropertyAnimation 脈動效果（opacity 1.0→0.45→1.0，900ms InOutSine）
- [x] 輸出區塊複製成功時加入短暫背景高亮（ACCENT_BG，600ms）

### 設定 API Key 並端對端測試
- [x] 建立 `.env`，填入 `OPENROUTER_API_KEY`
- [x] 執行整合測試，實際呼叫 `google/gemini-3-flash-preview`（4.4s）
- [x] 驗證輸出 prompt 包含 `--niji 7 --s 750` 與 `--ar 9:16`

---

## Phase 3 — 未來擴充

### 模板系統
- [ ] 新增第二個模板（例如 `stable-diffusion.json`），驗證零改程式碼
- [ ] 模板選擇器顯示（目前單模板自動隱藏）

### 功能
- [ ] 歷史記錄（LocalStorage 或 SQLite，最近 20 筆）
- [ ] 模型切換 UI（StatusBar ComboBox，切換 `active_model`）
- [ ] 自訂繪師輸入（允許手動輸入任意繪師名）

### 基礎建設
- [ ] FastAPI wrapper（將 PromptService 包成 REST API，為未來 Web 版準備）
- [ ] 打包為 `.exe`（PyInstaller / Nuitka）
