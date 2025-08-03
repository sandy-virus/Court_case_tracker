from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
import requests
from bs4 import BeautifulSoup


url = "https://delhihighcourt.nic.in/app/get-case-type-status"
raw_html = requests.get(url).text

def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # Fixed headless
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def case_type_options():
    soup = BeautifulSoup(raw_html, "html.parser")

    options = soup.select("#case_type option")

    case_types = [opt.text.strip() for opt in options if opt.get("value")]
    # print(case_types)
    return case_types


def fetch_case_selenium(case_type: str, case_number: str, filing_year: str):
    driver = get_driver()
    driver.get(url)
    # Wait until document.readyState is 'complete'
    
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page fully loaded!")
        
    except TimeoutException:
        print("Website can't be loaded")
        return None
    

    # Fill the form (adjust selectors as per website)
    driver.find_element(By.ID, "case_type").send_keys(case_type)
    driver.find_element(By.ID, "case_number").send_keys(case_number)
    driver.find_element(By.ID, "case_year").send_keys(filing_year)

    # Captcha Handling (manual or skip)
    try:
        captcha_text = driver.find_element(By.ID, "captcha-code").text
        driver.find_element(By.ID, "captchaInput").send_keys(captcha_text)
    except:
        print("Captcha handling required!")
    
    # time.sleep(2)

    # Submit
    element = driver.find_element(By.ID, "search")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)  # wait for scroll animation
    
    try:
        element.click()
    except ElementClickInterceptedException:
    # fallback to JS click if normal click blocked
        driver.execute_script("arguments[0].click();", element)

    time.sleep(3)
        
    # 7. Extract table rows
    rows = driver.find_elements(By.CSS_SELECTOR, "#caseTable tbody tr")
    result_data = []
    # print(len(rows))
    for idx, row in enumerate(rows, start=1):
        cols = row.find_elements(By.TAG_NAME, "td")
        # print("text in col: ", cols[0].text)
        if len(cols) < 4:
            print("No Data Found")
            continue

        case_info = cols[1].text.strip().split("\n")
        parties = cols[2].text.strip().split("\n")
        listing_date_court = cols[3].text.strip().split("\n")
        
        # PROCESS DATA
        case_info = " ".join(case_info).strip()
        
        petitioner = parties[0]
        respondent = parties[-1]
        
        next_hearing = listing_date_court[0].split()[-1]
        last_hearing = listing_date_court[1].split()[-1]
        # print("last_hearing: " + last_hearing + "\n" + "next_hearing: " + next_hearing)
        
        # pdf link
        link_tag = cols[1].find_elements(By.TAG_NAME, "a")
        latest_order_url = link_tag[1].get_attribute("href") if link_tag else None
        # print(latest_order_url)
        if latest_order_url is not None:
            pdfs = download_pdfs_from_new_tab(driver, latest_order_url)
       

        row_dict = {
            "case_info": case_info,
            "parties": parties,
            "listing_date_court": listing_date_court,
            "petitioner": petitioner,
            "respondent": respondent,
            "last_hearing": last_hearing,
            "next_hearing": next_hearing,
            "latest_order_url" : latest_order_url,
            "pdfs": pdfs,
            "raw_html" : raw_html
        }
        result_data.append(row_dict)
        # print(row_dict)

    driver.quit()
    return result_data


def download_pdfs_from_new_tab(driver, link_element) -> list:
    """
    Clicks a link that opens a new tab, scrapes all PDFs there, downloads them,
    closes the tab, and switches back to the original tab.
    """

    original_tab = driver.current_window_handle

    # Click the link to open new tab
    driver.execute_script(f"window.open('{link_element}', '_blank');")

    # Wait until new tab appears
    WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)

    # Switch to new tab (last handle)
    new_tab = [h for h in driver.window_handles if h != original_tab][0]
    driver.switch_to.window(new_tab)

    # print(f"Switched to new tab: {driver.current_url}")

    downloaded_files = []

    try:
        # Find all PDF links 
        pdf_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href,'.pdf')]"))
        )

        # print(f"Found {len(pdf_links)} PDF links on this page")

        for idx, pdf in enumerate(pdf_links, start=1):
            pdf_url = pdf.get_attribute("href")
            # print(pdf_url)
            if not pdf_url or ".pdf" not in pdf_url.lower():
                continue
            downloaded_files.append(pdf_url)

            

    except TimeoutException:
        print("No PDFs found in new tab")

    # Close new tab and switch back to original tab
    driver.close()
    driver.switch_to.window(original_tab)
    # print("Back to original tab")

    return downloaded_files