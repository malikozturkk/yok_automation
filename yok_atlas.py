from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

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

driver = webdriver.Chrome()
driver.get("https://yokatlas.yok.gov.tr/lisans-univ.php?u=2001")
time.sleep(3)

panels = driver.find_elements(By.CLASS_NAME, "panel-heading")

final_result = []

for i in range(len(panels)):
    panels = driver.find_elements(By.CLASS_NAME, "panel-heading")
    try:
        panels[i].click()
        time.sleep(2)

        detail_url = driver.current_url
        print(f"Gidilen detay sayfası: {detail_url}")

        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'featherlight-close'))
            )
            close_button.click()
            time.sleep(1)
        except:
            pass

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

                try:
                    modal = driver.find_element(By.CLASS_NAME, "featherlight")
                    if modal.is_displayed():
                        close_button = driver.find_element(By.CLASS_NAME, "featherlight-close")
                        close_button.click()
                        time.sleep(1)
                except:
                    pass

                sidebar_link = driver.find_element(By.XPATH, "//a[@href='#c1000_1']")
                sidebar_link.click()
                time.sleep(1)

                table_section = driver.find_element(By.ID, "c1000_1")
                rows = table_section.find_elements(By.TAG_NAME, "tr")

                cells = []
                for row in rows:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if len(tds) >= 2:
                        cells.append(tds[1].text.strip())

                if len(cells) < 23:
                    print(f"{year} yılı için yeterli veri yok, atlanıyor.")
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

                print(f"{year} verileri başarıyla işlendi.")

            except Exception as e:
                print(f"{year} yılı için hata: {str(e)}")

        print("Toplanan yearly_data:")
        print(json.dumps(yearly_data, indent=2, ensure_ascii=False))

        final_result.append({
            "detail_url": detail_url,
            "yearly_data": yearly_data
        })

    except Exception as e:
        print(f"Panel tıklama hatası: {str(e)}")

driver.quit()