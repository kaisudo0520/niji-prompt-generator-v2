# Niji Prompt Generator v2

輸入簡短描述，透過 LLM 自動補全各欄位，輸出可直接貼入 Midjourney 的 `--niji 7` 提示詞。

![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.x-green)
![LLM](https://img.shields.io/badge/LLM-Gemini%203%20Flash-orange)

---

## 功能

- **動態表單** — 根據 JSON 模板自動渲染繪師選擇、比例、色調等選項
- **LLM 補全** — 透過 OpenRouter 呼叫 Gemini 3 Flash Preview 補全所有提示詞欄位
- **一鍵複製** — 輸出完整 Midjourney 指令，複製後可直接貼上
- **可擴充模板** — 新增模板只需新增一個 JSON 檔案，不改任何程式碼

---

## 快速開始

### 1. 環境需求

- **Python 3.10**（注意：3.12 在部分 Windows 系統與 PySide6 有 DLL 相容問題）
- OpenRouter API Key（[申請連結](https://openrouter.ai/keys)）

### 2. 安裝

```bash
# 建立虛擬環境（指定 Python 3.10）
py -3.10 -m venv .venv
.venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 3. 設定 API Key

```bash
copy .env.example .env
```

開啟 `.env`，填入你的 OpenRouter API Key：

```
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxx
```

### 4. 啟動

```bash
# 生產模式（需要 API Key）
python main.py

# 開發預覽模式（不需 API Key，使用 Mock 資料）
python dev_preview.py
```

---

## 使用方式

1. 在左側「描述你的角色 / 場景」輸入簡短描述（中英文皆可）
2. 選擇 1~2 位參考繪師
3. 選擇圖像比例（預設 9:16）
4. 可選：選擇主色調，或留空讓 LLM 自動決定
5. 點擊「✦ 生成提示詞」
6. 右側顯示結果後，點擊「複製提示詞」貼入 Midjourney

---

## 開發

### 執行測試

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=src/services --cov=src/models
```

目前測試狀態：**24 passed**，覆蓋率 **83%**

### 開發預覽（無 LLM）

```bash
python dev_preview.py
```

不需要 API Key，點擊「生成」後回傳固定 Mock 結果，方便 UI 開發調試。

---

## 專案結構

```
niji-prompt-generator-v2/
├── src/
│   ├── ui/                    # PySide6 UI 層
│   │   ├── styles/theme.py    # Ink Garden 深色主題 QSS
│   │   ├── widgets/           # 元件（DynamicForm, PromptOutput 等）
│   │   │   └── inputs/        # 可複用輸入元件
│   │   ├── workers/           # QThread 背景工作
│   │   └── main_window.py
│   ├── services/              # 業務邏輯（無 UI 依賴，可獨立測試）
│   │   ├── template_service.py
│   │   ├── llm_service.py     # OpenRouter HTTP 客戶端
│   │   └── prompt_service.py
│   └── models/                # Pydantic 資料模型（即規格文件）
├── templates/                 # JSON 模板（新增模板只需加此處）
│   └── niji-anime.json
├── config/
│   └── llm_config.json        # 模型設定（可切換）
├── tests/
├── dev_preview.py             # 開發用預覽（無需 API Key）
├── main.py                    # 生產進入點
└── TODO.md                    # 開發進度追蹤
```

---

## 模板設定

模型設定在 `config/llm_config.json`：

```json
{
  "active_model": "google/gemini-3-flash-preview",
  "available_models": [
    { "id": "google/gemini-3-flash-preview", "name": "Gemini 3 Flash Preview" }
  ]
}
```

修改 `active_model` 即可切換模型，無需改程式碼。

---

## 新增模板

1. 在 `templates/` 建立新 JSON 檔案（參考 `niji-anime.json` 格式）
2. 重啟程式，新模板自動載入

不需修改任何 Python 程式碼。
