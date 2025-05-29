from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://yokatlas.yok.gov.tr/lisans-univ.php?u=2001")
time.sleep(3)

panels = driver.find_elements(By.CLASS_NAME, "panel-heading")

for i in range(len(panels)):
    panels = driver.find_elements(By.CLASS_NAME, "panel-heading")
    
    try:
        panels[i].click()
        time.sleep(3)

        detail_url = driver.current_url
        print(f"Gidilen detay sayfası: {detail_url}")

        try:
            close_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'featherlight-close'))
            )
            close_button.click()
            print("Modal kapatıldı.")
        except:
            print("Kapatılacak modal bulunamadı, devam ediliyor...")

        try:
            button_2022 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(., '2022 Yılı')]"))
            )
            button_2022.click()
        except:
            print("2022 Yılı linki bulunamadı, atlanıyor...")
            continue

        sidebar_link = driver.find_element(By.XPATH, "//a[@href='#c1000_1']")
        sidebar_link.click()
        time.sleep(2)

        table = driver.find_element(By.ID, "c1000_1")
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = {}
        for row in rows:
            try:
                tds = row.find_elements(By.TAG_NAME, "td")
                key = tds[0].text.strip()
                value = tds[1].text.strip()
                data[key] = value
            except:
                continue

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

        result = {
            "yearly_data": [
                {
                    "year": 2022,
                    "quota": parse_int(data.get("Toplam Kontenjan", "0")),
                    "placement": parse_int(data.get("Toplam Yerleşen", "0")),
                    "base_score": parse_float(data.get("0,12 Katsayı ile Yerleşen Son Kişinin Puanı*", "0")),
                    "top_score": parse_float(data.get("2022 Tavan Puan(0,12)*", "0")),
                    "base_rank": parse_int(data.get("0,12 Katsayı ile Yerleşen Son Kişinin Başarı Sırası*", "0")),
                    "top_rank": parse_int(data.get("2022 Tavan Başarı Sırası(0,12)*", "0")),
                }
            ]
        }

        print("-----")
        print(result)
        print("-----")

        driver.back()
        time.sleep(3)

    except Exception as e:
        print(f"Hata oluştu: {e}")
        driver.back()
        time.sleep(3)

driver.quit()
