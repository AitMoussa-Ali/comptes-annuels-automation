# CLAUDE.md — Project Context & Source of Truth

> This file is the single source of truth for the "Comptes Annuells" backend project.
> Always read this file before answering any question or producing any output.
> Update it whenever decisions, architecture, or context change.

---

## Project Overview

**Project name:** Comptes Annuells (Annual Accounts)
**Company:** Groupe Aplitec
**Type:** Python backend API
**Purpose:** Automate the retrieval and processing of annual account documents stored in Microsoft SharePoint, accessed via the Microsoft Graph API.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.14.4 |
| Runtime | CPython (venv at project root) |
| Auth | MSAL (Microsoft Authentication Library) — client credentials flow |
| HTTP | `requests` library |
| Data | `pandas` + `openpyxl` for Excel parsing |
| Config | `python-dotenv` (`.env` file, never committed) |
| External API | Microsoft Graph API v1.0 |
| Storage | Microsoft SharePoint (OneDrive/Drive API) |

---

## Project Structure

```
backend/
├── CLAUDE.md                        ← this file
├── Config.py                        ← centralised env-var config class
├── Routes/
│   └── FondsRoutes.py               ← API routes for "Fonds" (empty/WIP)
├── Sharepoint_Handler/
│   ├── Requests.py                  ← Graph API auth + drive helpers
│   └── Read_excel.py                ← reads Excel files from SharePoint
├── .gitignore                       ← venv-generated (ignores everything)
├── pyvenv.cfg                       ← Python 3.14.4 virtual environment
├── Scripts/                         ← venv scripts (python.exe, pip, etc.)
└── Lib/                             ← venv installed packages
```

---

## Configuration (`Config.py`)

All configuration is loaded from a `.env` file via `python-dotenv`. **Never commit `.env`.**

| Variable | Purpose |
|---|---|
| `CLIENT_ID` | Azure AD app registration client ID |
| `CLIENT_SECRET` | Azure AD app client secret |
| `TENANT_ID` | Azure AD tenant ID |
| `SHARED_MAILBOX` | Shared mailbox address (email-related operations) |
| `SCOPES` | Microsoft Graph API scope (e.g. `https://graph.microsoft.com/.default`) |
| `PASSWORD_MAILBOX` | Mailbox password (used as `client_credential` in MSAL — likely same as `CLIENT_SECRET`) |
| `URL_SHARE_POINT` | SharePoint base URL |
| `SHAREPOINT_FOLDER` | Target folder path in SharePoint |
| `SHAREPOINT_FOLDER_EXCEL` | Folder path for Excel files in SharePoint |
| `SHAREPOINT_SITE_URL` | SharePoint site URL for Graph API (format: `tenant.sharepoint.com:/sites/sitename`) |
| `PATH_LOGIN_FILE` | Path to the login/reference Excel file in SharePoint |
| `SHEET_LOGIN_NAME` | Filename of the login/reference Excel sheet |
| `LOCAL_PATH_LOGIN_FILE_SHEET` | Local path for the login file (if applicable) |
| `SENDER` (→ `MAIL_SENDER`) | Email sender address |

---

## Key Modules

### `Sharepoint_Handler/Requests.py`

- **`get_token() → str | None`**: Authenticates against Azure AD using MSAL client credentials flow. Returns a bearer token or `None` on failure.
- **`get_drive_id(token) → str`**: Resolves the SharePoint site ID via Graph API, then returns the first drive ID for that site.
- **`get_drive_id_excel(token) → str`**: Alternative drive ID resolver using `/drives` endpoint directly (returns first drive from root). Likely a WIP/fallback.

### `Sharepoint_Handler/Read_excel.py`

- **`read_excel_from_sharepoint() → pd.DataFrame | None`**: Full pipeline — gets token, resolves drive, downloads the Excel file from SharePoint, parses it with `pandas` (skipping first row), returns a DataFrame.
- Currently has a `print(read_excel_from_sharepoint())` at module level — this is a debug/test call that should be removed before production use.

### `Sharepoint_Handler/Upload.py`

- **`upload_file_to_sharepoint(filename, content, fond_name) → bool`**: Uploads raw bytes to SharePoint under `{SHAREPOINT_FOLDER}/{fond_name}/{filename}` using Graph API `PUT`. Returns `True` on 200/201.

### `Controllers/UploadController.py`

- **File rules** — `FILES_ANCIENNETE_A` (4 files) and `FILES_ANCIENNETE_N` (2 files) are dicts mapping form field keys to SharePoint filenames.
- **`UploadFondFiles()`** — validates all required files are present, uploads each to SharePoint, raises 422 on missing files, 502 on upload failure.
- Files are stored as `{label}.{original_extension}` inside a fund-specific subfolder.

### `Routes/UploadRoutes.py`

- **`POST /upload/`** — multipart/form-data endpoint.
  - Form fields: `fond_name: str`, `anciennete: str` ("A" or "N")
  - File fields (all optional at HTTP layer, validated in controller):
    - `fichier_vl_n` — required for A and N
    - `fichier_vl_n_1` — required for A only
    - `balance_n_1` — required for A only
    - `comptes_annuels_n_1` — required for A only
    - `comptes_resultats_vide` — required for N only
  - Response: `UploadResponse { success, fond_name, uploaded_files, message }`

### `Routes/FondsRoutes.py`

- **`GET /fonds/`** — returns a paginated list of funds read from the SharePoint Excel file.
  - Query params: `page` (int, ≥1, default 1), `page_size` (int, 1–100, default 10)
  - Response model: `FondsResponse` → `{ total, page, page_size, total_pages, data: [Fond] }`
  - `Fond` model: `{ nom: str, anciennete: Optional[str] }`
  - Columns are accessed positionally (iloc[:, :2]) — column 1 = fund name, column 2 = ancienneté du fond.
  - Returns HTTP 503 if the SharePoint read fails.

---

## Authentication Flow

The app uses **OAuth 2.0 Client Credentials** (daemon/service-to-service):
1. MSAL `ConfidentialClientApplication` with `CLIENT_ID` + `PASSWORD_MAILBOX` (secret)
2. Token requested for `SCOPES` (Graph API)
3. Bearer token used on all subsequent Graph API calls

No user interaction — fully automated service account flow.

---

## Known Issues / TODOs

- `Routes/FondsRoutes.py` is empty — routes need to be implemented.
- `get_drive_id_excel()` in `Requests.py` calls `/drives` without site context — likely incorrect or incomplete.
- ~~`Read_excel.py` has a bare `print()` call at module level~~ — **fixed**, removed.
- **Framework: FastAPI** — confirmed by user. Routes use `APIRouter`. A `main.py` entry point still needs to be created to mount the routers.
- `PASSWORD_MAILBOX` is used as the MSAL `client_credential` — this naming is confusing; it should likely be `CLIENT_SECRET`.

---

## Decisions & Conventions

- **Config is centralised in `Config.py`** — all modules import from there, never read env vars directly.
- **Virtual environment lives at the project root** — `Scripts/`, `Lib/`, `pyvenv.cfg` are all at `backend/`.
- **`.gitignore` ignores everything** (venv-generated `*` rule) — project source files must be explicitly tracked or a proper `.gitignore` added.

---

## Evolution Log

| Date | Change |
|---|---|
| 2026-06-15 | Initial CLAUDE.md created from project scan. Project is in early development: config + SharePoint auth/read layer exists, routes layer is empty, no web framework wired yet. |
| 2026-06-15 | Added `GET /fonds/` route with pagination in `FondsRoutes.py`. Framework confirmed as FastAPI. Removed debug `print()` from `Read_excel.py`. |
| 2026-06-15 | Added `POST /upload/` route. Created `Sharepoint_Handler/Upload.py`, `Controllers/UploadController.py`, `Routes/UploadRoutes.py`. File requirements: ancienneté A → 4 files, N → 2 files. |
