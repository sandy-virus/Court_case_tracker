# 🏛 Court Case Scraper – FastAPI + Selenium

## 📌 Project Overview
A **FastAPI + Selenium** web application to **search Delhi High Court case details** by:

- **Case Type**  
- **Case Number**  
- **Filing Year**  

The application:

- **Scrapes live court data** using **Selenium**  
- **Stores queries & results** in **SQLite (via SQLAlchemy)**  
- **Displays results** in a **web UI with Jinja2 templates**  
- Supports **PDF extraction** of the latest court orders

---

## ⚡ Tech Stack

- **FastAPI** – Backend & form handling  
- **Selenium** – Scraping dynamic JavaScript-heavy court website  
- **SQLAlchemy + SQLite** – Database storage & ORM  
- **Jinja2** – HTML templating for frontend  
- **BeautifulSoup** – Initial static case-type extraction  

---

## 💡 Why FastAPI & Selenium?

**FastAPI**  
- Extremely **fast & async** friendly  
- Easy **HTML form & template rendering**  
- Integrates well with **threaded tasks** using `run_in_threadpool`

**Selenium**  
- Court sites load data **via JS & AJAX** → `requests` fails  
- Needed **form interaction & click handling**  
- Supports **PDF extraction via new tab handling**

---

## 📂 Folder Structure

```
court-case-scraper/
│
├── main.py                # FastAPI app & routing
├── scraper.py             # Selenium scraping logic
├── database.py            # SQLite connection & setup
├── models.py              # SQLAlchemy ORM models
├── templates/
│   └── index.html         # UI template
├── court_cases.db         # SQLite DB (auto-created)
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

---

## 🗄 Database Design

**Tables:**

1. **CaseResult**
   - Stores **unique case info**  
   - Columns: `petitioner`, `respondent`, `last_hearing`, `next_hearing`, `latest_order_url`  

2. **CaseQuery**
   - Stores **each user search**  
   - Columns: `case_type`, `case_number`, `filing_year`, `response_html`, `created_at`  
   - Linked to `CaseResult` via **ForeignKey (result_id)**  

**ER Diagram:**

```
CaseResult (1) ─────< (many) CaseQuery
```

- **One case** can have **multiple queries** without duplicating data

---

## 🔄 Scraper Flow Diagram

```
[User Form Submit]
        |
        v
 FastAPI (POST /search)
        |
        v
run_scraper_and_save() ──> Selenium WebDriver
        |                          |
        |                   1. Load Delhi HC page
        |                   2. Fill form (case type, number, year)
        |                   3. Handle captcha (if any)
        |                   4. Click search
        |                   5. Extract case table & PDF links
        v
    Save to SQLite
        |
        v
 Rendered in index.html
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your_repo_url>
   cd court-case-scraper
   ```

2. **Create & activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate     # Mac/Linux
   venv\Scripts\activate        # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```
   Visit: **http://127.0.0.1:8000/**

---

## 😓 Challenges & Solutions

| **Challenge**                                | **Solution** |
|----------------------------------------------|--------------|
| Selenium blocking FastAPI event loop          | Used `ThreadPoolExecutor` + `run_in_threadpool` |
| Dynamic JS-based content not loading          | Added `WebDriverWait` for `document.readyState` |
| Duplicate case data in DB                     | Filtered existing entries before insert |
| PDF links opening in new tab                  | Implemented `download_pdfs_from_new_tab` to scrape & return URLs |
| Captcha handling                              | Currently logged message; future plan to automate |

---

## 🚀 Future Improvements

- **Captcha automation** with OCR / AI  
- **Async PDF downloading & caching**  
- **Docker + Cloud Deployment**  
