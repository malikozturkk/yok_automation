from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import re

def parse_int(val):
    try:
        return int(val.replace('.', '').replace(',', '').strip())
    except:
        return None

def parse_float(val):
    try:
        return float(val.replace(',', '.').strip())
    except:
        return None
    

score_type_map = {
    "SAY": "numerical",
    "EA": "equal_weight",
    "SÖZ": "verbal",
    "TYT": "tyt"
}

def extract_language_and_clean_name(name: str):
    language = "Türkçe" 
    language_list = ["İngilizce", "Almanca", "Fransızca", "Rusça", "İtalyanca", "Arapça"]
    for lang in language_list:
        if f"({lang})" in name:
            language = lang
            name = name.replace(f"({lang})", "").strip()
            break
    name = re.sub(r'\s+', ' ', name)
    return name, language

def extract_education_type(name: str):
    if "(İÖ)" in name:
        return "second_education"
    elif "(Uzaktan Öğretim)" in name:
        return "distance"
    else:
        return "formal"
    

driver = webdriver.Chrome()
driver.get("https://yokatlas.yok.gov.tr/lisans-univ.php?u=2001")
time.sleep(3)

panel_links = []
panels = driver.find_elements(By.CLASS_NAME, "panel-heading")
for panel in panels:
    try:
        a_tag = panel.find_element(By.TAG_NAME, "a")
        href = a_tag.get_attribute("href")
        if href:
            panel_links.append(href)
    except:
        continue


final_result = []

for index, detail_url in enumerate(panel_links):
    driver.get(detail_url)
    time.sleep(2)

    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'featherlight-close'))
        )
        close_button.click()
        time.sleep(1)
    except:
        pass

    try:
        title_element = driver.find_element(By.CSS_SELECTOR, "div.panel.panel-primary h2.panel-title.pull-left")
        raw_title = title_element.text.strip()
        if "Program :" in raw_title:
            name = raw_title.split(" - ", 1)[-1].strip()
        else:
            name = raw_title

        name, language = extract_language_and_clean_name(name)
        education_type = extract_education_type(name)
        
    except Exception as e:
        print(f"Name verisi alınamadı: {str(e)} ({detail_url})")
        name = ""
        language = "Türkçe"
        education_type = "formal"

    try:
        score_type_element = driver.find_element(By.CSS_SELECTOR, "div.panel.panel-primary h3.panel-title.pull-right")
        raw_score_type = score_type_element.text.strip()
        match = re.search(r"Puan Türü:\s*(\w+)", raw_score_type)
        score_type_code = match.group(1) if match else ""
        score_type = score_type_map.get(score_type_code, "") 
    except Exception as e:
        print(f"Score type alınamadı: {str(e)} ({detail_url})")
        score_type = ""

    try:
        faculty_element = driver.find_element(By.CSS_SELECTOR, "div.panel[style*='background-color:#e1e1e1;'] h3.panel-title.pull-left")
        full_text = faculty_element.text.strip()

        faculty = full_text.split(":", 1)[1].strip() if ":" in full_text else full_text
    except Exception as e:
        print(f"Faculty verisi alınamadı: {str(e)} ({detail_url})")
        faculty = ""


    yearly_data = []

    for year in [2022, 2023, 2024]:
        try:
            try:
                modal = driver.find_element(By.CLASS_NAME, "featherlight")
                if modal.is_displayed():
                    close_button = driver.find_element(By.CLASS_NAME, "featherlight-close")
                    close_button.click()
                    time.sleep(1)
            except:
                pass

            year_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, f"//a[contains(., '{year} Yılı')]"))
            )
            year_button.click()
            time.sleep(2)

            if "File not found" in driver.page_source:
                print(f"{year} yılı için veri yok (File not found). Sonraki yıla geçiliyor. ({detail_url})")
                driver.back() 
                time.sleep(2)
                continue

            try:
                modal = driver.find_element(By.CLASS_NAME, "featherlight")
                if modal.is_displayed():
                    close_button = driver.find_element(By.CLASS_NAME, "featherlight-close")
                    close_button.click()
                    time.sleep(1)
            except:
                pass

            sidebar_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='#c1000_1']"))
            )
            sidebar_link.click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "c1000_1"))
            )
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_element(By.ID, "c1000_1").find_elements(By.TAG_NAME, "td")) >= 23
            )

            table_section = driver.find_element(By.ID, "c1000_1")
            rows = table_section.find_elements(By.TAG_NAME, "tr")

            cells = []
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    cells.append(tds[1].text.strip())

            if len(cells) < 23:
                print(f"{year} yılı için yeterli veri yok, atlanıyor. ({detail_url})")
                continue

            yearly_data.append({
                "year": year,
                "quota": parse_int(cells[8]),
                "base_score": parse_float(cells[16]),
                "top_score": parse_float(cells[20]),
                "base_rank": parse_int(cells[18]),
                "top_rank": parse_int(cells[21]),
                "placement": parse_int(cells[11])
            })

        except Exception as e:
            print(f"{year} yılı için hata: {str(e)} ({detail_url})")

    final_result.append({
        "name": name,
        "faculty": faculty,
        "language": language,
        "duration": "4 yıl",
        "degree_level": "licence",
        "score_type": score_type,
        "education_type": education_type,
        "yearly_data": yearly_data
    })
    
    with open("acibadem.json", "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
driver.quit()