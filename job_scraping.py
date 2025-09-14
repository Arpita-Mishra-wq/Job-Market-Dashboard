import re
import pandas as pd # type: ignore
import time
import random
import os

from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.chrome.service import Service # type: ignore
from webdriver_manager.chrome import ChromeDriverManager # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore

role="Data Analyst"
city=None
pages=5

headless=False
delay_range=(1.5,3.5)

out_csv="jobs_data.csv"

def slugify(text: str)->str:
    text=text.lower().strip()
    text=re.sub(r"[^a-z0-9]+","-", text)
    return text.strip("-")

def build_url(role: str, city: str | None, page: int)-> str:
    q=slugify(role)
    if city:
        c=slugify(city)
        base=f"https://www.naukri.com/{q}-jobs-in-{c}"
    else:
        base=f"https://www.naukri.com/{q}-jobs"
    if page>1:
        return f"{base}-{page}"
    return base

def get_text(node, css: str):
    try:
        return node.find_element(By.CSS_SELECTOR, css).text.strip()
    except Exception:
        return None
    
def get_attr(node, css: str, attr: str):
    try:
        return node.find_element(By.CSS_SELECTOR, css).get_attribute(attr)
    except Exception:
        return None
    
#selenium driver setup
def make_driver(headless:bool=True):
    options=webdriver.ChromeOptions() # type:ignore
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,2000")
    options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    service=Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service,options=options) # type: ignore

def scrape_pg(driver,url:str)->list[dict]:
    driver.get(url)

    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

    wait=WebDriverWait(driver,10)

    selectors_possible = ["div.srp-jobtuple-wrapper","div.cust-job-tuple","div.cust-job-card", "div.jobTuple","div.srp-jobtuple","div.srp-joblist__item","article",]

    found=False
    for sel in selectors_possible:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if cards:
                found=True
                break
        except Exception:
            continue

    if not found:
        return []

    rows = []
    for card in cards:
        title = (
            get_text(card, "a.title") or
            get_text(card, "a.title.ellipsis") or
            get_text(card, "a[href*='jobs']")
        )
        link = (
            get_attr(card, "a.title", "href") or
            get_attr(card, "a.title.ellipsis", "href") or
            get_attr(card, "a[href*='jobs']", "href")
        )
        company = (
            get_text(card, "a.subTitle") or
            get_text(card, "span.comp-name") or
            get_text(card, "[class*='company']")
        )
        location = (
            get_text(card, "li.fleft.location") or
            get_text(card, "span.locWdth") or
            get_text(card, "[class*='location']")
        )
        experience = (
            get_text(card, "li.fleft.experience") or
            get_text(card, "span.expwdth") or
            get_text(card, "[class*='exp']")
        )
        salary = (
            get_text(card, "li.fleft.salary") or
            get_text(card, "span.salary") or
            get_text(card, "[class*='salary']")
        )
        posted = (
            get_text(card, "span.job-post-day") or
            get_text(card, "[class*='post-day']") or
            get_text(card, "[class*='posted']")
        )

        # skip empty rows
        if not any([title, company, location, experience, salary, posted, link]):
            continue

        rows.append(
            {
                "Title": title,
                "Company": company,
                "Location": location,
                "Experience": experience,
                "Salary": salary,
                "Posted": posted,
                "Link": link,
                "source_url": url,
            }
        )
    return rows

def main():
    driver=make_driver(headless)
    all_rows:list[dict]=[]
    try:
        for page in range(1,pages+1):
            url=build_url(role,city,page)
            print(f"[{page}/{pages}]{url}")
            page_rows=scrape_pg(driver, url)
            print(f"->found{len(page_rows)} cards")
            all_rows.extend(page_rows)
            time.sleep(random.uniform(*delay_range))
    finally:
        driver.quit()

    if not all_rows:
        print("No rows found.")
        return
    
    df=pd.DataFrame(all_rows).drop_duplicates()
    df.to_csv(out_csv, mode="a", header=not os.path.exists(out_csv), index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} rows to {out_csv}")

if __name__=="__main__":
    main()