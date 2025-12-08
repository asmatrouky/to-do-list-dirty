import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://127.0.0.1:8000/"
RESULT_FILE = "result_test_selenium.json"


def write_selenium_result(test_id, status, message=""):
    result = {test_id: status}
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"\n Résultat exporté dans {RESULT_FILE}")


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
    time.sleep(0.5)

    tasks = get_task_ids(driver)
    last_task = tasks[-1]
    return last_task[0], last_task[1]


def delete_last_task(driver):
    delete_btn = driver.find_elements(
        By.CSS_SELECTOR, 'a[href^="/delete_task/"]'
    )[-1]
    delete_btn.click()
    time.sleep(0.3)

    confirm_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    confirm_btn.click()
    time.sleep(0.4)


def main():
    TEST_ID = "TC017"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        driver.get(BASE_URL)
        time.sleep(1)

        # 1) Ajouter la première tâche
        print("Création de la tâche A…")
        taskA_id, taskA_title = create_task(driver, "Tâche A Selenium")
        print(f"Tâche A créée : id={taskA_id}, titre={taskA_title}")

        # 2) Ajouter une deuxième tâche
        print("Création de la tâche B…")
        taskB_id, taskB_title = create_task(driver, "Tâche B Selenium")
        print(f"Tâche B créée : id={taskB_id}")

        # 3) Suppression de la tâche B
        print("Suppression de la tâche B…")
        delete_last_task(driver)

        # 4) Vérifier que la tâche A existe toujours
        tasks_after = get_task_ids(driver)
        task_ids = [tid for tid, _ in tasks_after]

        assert taskA_id in task_ids, (
            f"ERREUR :  (id={taskA_id}) plus détectée "
        )

        print("\nSUCCESS : Test TC017 OK ")
        write_selenium_result(TEST_ID, "passed")

    except Exception as e:
        print("\nERROR SELENIUM :", e)
        write_selenium_result(TEST_ID, "failed")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
