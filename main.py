from fastapi.concurrency import run_in_threadpool
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from scraper import case_type_options, fetch_case_selenium
from database import SessionLocal
from models import CaseQuery, CaseResult

executor = ThreadPoolExecutor(max_workers=1)
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
CASE_TYPE_LIST = []
def run_scraper_and_save(case_type, case_number, filing_year):
    db = SessionLocal()
    
    try:
        # Fetch Selenium Results
        results = fetch_case_selenium(case_type, case_number, filing_year)

        if results:
            for result in results:
                existing_result = db.query(CaseResult).filter(
                CaseResult.petitioner==result.get("petitioner"),
                CaseResult.respondent==result.get("respondent"),
                CaseResult.last_hearing==result.get("last_hearing")
                ).first()
                # print(existing_result)

                if existing_result is None:
                    # make new result if the data is not present
                    # print("Databse new")
                    existing_result = CaseResult(
                        petitioner=result.get("petitioner"),
                        respondent=result.get("respondent"),
                        last_hearing=result.get("last_hearing"),
                        next_hearing=result.get("next_hearing"),
                        latest_order_url=result.get("latest_order_url")
                    )
                    db.add(existing_result)
                    db.commit()
                    db.refresh(existing_result)


                # now map the data
                query = CaseQuery(
                    case_type=case_type,
                    case_number=case_number,
                    filing_year=filing_year,
                    response_html=result.get("raw_html", ""),
                    result_id=existing_result.id   # 👈 foreign key mapping
                )
                db.add(query)
                db.commit()

        return results
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    global CASE_TYPE_LIST
    CASE_TYPE_LIST = case_type_options()
    # print(case_type)
    return templates.TemplateResponse("index.html", {"request": request, "case_type": CASE_TYPE_LIST})

@app.post("/search", response_class=HTMLResponse)
async def search_case(
    request: Request,
    case_type: str = Form(...),
    case_number: str = Form(...),
    filing_year: str = Form(...),
):
    result = await run_in_threadpool(
        run_scraper_and_save, case_type, case_number, filing_year
    )
    # Define which keys you want to keep
    keys_to_keep = ["case_info", "latest_order_url", "listing_date_court", "parties", "pdfs"]

    # Create a new list where only required keys are kept
    cleaned_data = []  

    for item in result:       
        new_dict = {}           
        for key in keys_to_keep:  
            if key in item:     
                new_dict[key] = item[key]
        cleaned_data.append(new_dict) 


    return templates.TemplateResponse("index.html", {
        "request": request,
        "case_type": CASE_TYPE_LIST,
        "case_data": cleaned_data if cleaned_data else None,
        "error": None if result else "No data found",
        "form_data": {
            "case_type": case_type,
            "case_number": case_number,
            "filing_year": filing_year
        }
    })