import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = "http://127.0.0.1:8000/"      
RESULT_FILE = "result_test_selenium.json"


# ✅ NOUVELLE VERSION
def write_selenium_result(test_id, status):
    result = {test_id: status}

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\n📄 Résultat exporté dans {RESULT_FILE}")


def count_tasks(driver):
    return len(driver.find_elements(By.CSS_SELECTOR, ".item-row"))


def main():
    TEST_ID = "TC016"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        print("Ouverture de l'application...")
        driver.get(BASE_URL)
        time.sleep(1)

        initial_count = count_tasks(driver)
        print(f"Nombre initial de tâches : {initial_count}")

        print("Création de 10 tâches...")
        for i in range(10):
            input_field = driver.find_element(By.ID, "id_title")
            input_field.clear()
            input_field.send_keys(f"Tâche Selenium {i}")
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)

        after_create = count_tasks(driver)
        print(f"Nombre après création : {after_create}")

        assert after_create == initial_count + 10, (
            f"ERREUR : après création, attendu {initial_count + 10}, obtenu {after_create}"
        )

        print("Suppression des 10 tâches...")
        for _ in range(10):
            delete_link = driver.find_elements(
                By.CSS_SELECTOR, 'a[href^="/delete_task/"]'
            )[0]
            delete_link.click()
            time.sleep(0.4)

            confirm_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            confirm_btn.click()
            time.sleep(0.4)

        final_count = count_tasks(driver)
        print(f"Nombre final après suppression : {final_count}")

        assert final_count == initial_count, (
            f"ERREUR : après suppression, attendu {initial_count}, obtenu {final_count}"
        )

        print("\n SUCCESS : Test E2E Selenium OK")
        write_selenium_result(TEST_ID, "passed")

    except Exception as e:
        print("\n ERROR SELENIUM :", e)
        write_selenium_result(TEST_ID, "failed")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
