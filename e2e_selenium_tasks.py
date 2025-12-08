import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000/"
RESULT_FILE = "result_test_selenium.json"

def create_driver():
    options = Options()
    options.add_argument("--headless")               
    options.add_argument("--no-sandbox")            
    options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def write_selenium_result(test_id, status):
    try:
        # Charger l'ancien JSON s'il existe
        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                content = json.load(f)
        except FileNotFoundError:
            content = {}

        content[test_id] = status

        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

        print(f"📄 Résultat mis à jour dans {RESULT_FILE}")

    except Exception as e:
        print("❌ ERREUR lors de l'écriture du fichier JSON :", e)


def count_tasks(driver):
    return len(driver.find_elements(By.CSS_SELECTOR, ".item-row"))


def get_task_ids(driver):
    items = driver.find_elements(By.CSS_SELECTOR, ".item-row")
    tasks = []

    for item in items:
        tid = item.get_attribute("data-task-id")
        ttitle = item.get_attribute("data-task-title")
        tasks.append((tid, ttitle))

    return tasks


def create_task(driver, title):
    input_field = driver.find_element(By.ID, "id_title")
    input_field.clear()
    input_field.send_keys(title)
    input_field.send_keys(Keys.RETURN)
    time.sleep(0.4)

    tasks = get_task_ids(driver)
    last = tasks[-1]
    return last[0], last[1]


def delete_last_task(driver):
    delete_btn = driver.find_elements(
        By.CSS_SELECTOR, 'a[href^="/delete_task/"]'
    )[-1]
    delete_btn.click()
    time.sleep(0.3)

    confirm = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    confirm.click()
    time.sleep(0.3)


#  TEST TC016 — Création de 10 tâches + suppression + comptage final
def run_tc016(driver):
    TEST_ID = "TC016"

    try:
        print("\n=== TC016 : Test création + suppression de 10 tâches ===")
        driver.get(BASE_URL)
        time.sleep(1)

        initial = count_tasks(driver)
        print(f"Tâches initiales : {initial}")

        # Créer 10 tâches
        for i in range(10):
            input_field = driver.find_element(By.ID, "id_title")
            input_field.clear()
            input_field.send_keys(f"Tâche Selenium {i}")
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.4)

        after_create = count_tasks(driver)
        print(f"Après création : {after_create}")

        assert after_create == initial + 10, (
            f"Attendu {initial + 10}, obtenu {after_create}"
        )

        # Supprimer les 10 dernières tâches
        for _ in range(10):
            delete_last_task(driver)

        final = count_tasks(driver)
        print(f"Après suppression : {final}")

        assert final == initial, (
            f"Attendu {initial}, obtenu {final}"
        )

        print("SUCCESS TC016")
        write_selenium_result(TEST_ID, "passed")

    except Exception as e:
        print("ERROR TC016 :", e)
        write_selenium_result(TEST_ID, "failed")


#  TEST TC017 — Vérifier que supprimer la dernière tâche ne supprime pas la mauvaise
def run_tc017(driver):
    TEST_ID = "TC017"

    try:
        print("\n=== TC017 : Vérification suppression correcte ===")
        driver.get(BASE_URL)
        time.sleep(1)

        # Créer tâche A
        taskA_id, _ = create_task(driver, "Tâche A Selenium")
        print(f"Tâche A créée : id={taskA_id}")

        # Créer tâche B
        taskB_id, _ = create_task(driver, "Tâche B Selenium")
        print(f"Tâche B créée : id={taskB_id}")

        # Suppression de B
        delete_last_task(driver)

        # Vérification
        remaining_ids = [tid for tid, _ in get_task_ids(driver)]
        assert taskA_id in remaining_ids, (
            f"ERREUR : La tâche A (id={taskA_id}) aurait dû rester."
        )

        print("SUCCESS TC017")
        write_selenium_result(TEST_ID, "passed")

    except Exception as e:
        print("ERROR TC017 :", e)
        write_selenium_result(TEST_ID, "failed")


def main():
    driver = create_driver()
    driver.maximize_window()

    try:
        run_tc016(driver)
        run_tc017(driver)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
