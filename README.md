# Invoice / POS Mini System (Tkinter + SQLite + reportlab)

This is a minimal desktop Invoice/POS app built with Tkinter (GUI), SQLite (database), and reportlab (PDF export).

Quick start

1. Create a Python environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
python main.py
```

3. Add products, then create an invoice and click "Save Invoice (PDF)". PDFs are saved to the `invoices` folder.

Packaging to .exe (Windows)

Install PyInstaller and run:

```powershell
pip install pyinstaller
pyinstaller --onefile --add-data "invoices;invoices" main.py
```

Notes

- GUI code is in `main.py`.
- Database helpers are in `db.py` (creates `bank_db.db`).
- PDF export is in `pdf_invoice.py`.

Automatic local rebuilds

Install the watcher dependency:

```powershell
pip install watchdog
```

Run the watcher to rebuild `main.exe` whenever source files change:

```powershell
python build_watcher.py
```

To run a single rebuild (non-blocking):

```powershell
python build_watcher.py --once
```
