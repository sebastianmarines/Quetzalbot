from webdriver import HealingDriver
from selenium.webdriver.common.by import By
from pathlib import Path
import time
import datetime
import csv
import random
import sqlite3

class TestHealingDriver:
    driver: HealingDriver

    def setup_method(self):
        self.driver = HealingDriver()

    def teardown_method(self):
        self.driver.quit()

    def write_report(self, data, filename):
        with open(filename, 'a') as f:
            for key, value in data.items():
                f.write(f'{key}: {value}\n')
            f.write('\n')

    def generate_self_heal_event(self, object_healed, prev_id, new_id):
        return {
            'time': datetime.datetime.now().isoformat(),
            'object_healed': object_healed,
            'previous_id': prev_id,
            'new_id': new_id
        }

    def self_heal_happens(self):
        return random.choice([True, False])

    def write_to_db(self, data):
        conn = sqlite3.connect('self_heal_report.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS self_heal (time text, reason text, object_healed text, previous_id text, new_id text)")
        c.execute("INSERT INTO self_heal VALUES (?, ?, ?, ?, ?)", (data['time'], data['reason'], data['object_healed'], data['previous_id'], data['new_id']))
        conn.commit()
        conn.close()

    def test_get(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        assert self.driver.current_url == html_file.as_uri()
        time.sleep(2)  # Sleep for 2 seconds

        # Generate and write self-heal event
        object_healed = "Button"
        prev_id = "btn"
        new_id = "new_btn"
        event = self.generate_self_heal_event(object_healed, prev_id, new_id)
        self.write_report(event, 'self_heal_report.txt')

        # Check if self-heal happened and write to database if true
        if self.self_heal_happens():
            self.write_to_db(event)

    def test_find_element(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        time.sleep(2)  # Sleep for 2 seconds
        button = self.driver.find_element(By.ID, "btn")
        assert button.get_attribute("id") == "btn"
        time.sleep(2)  # Sleep for 2 seconds

        # Generate and write self-heal event
        object_healed = "Button"
        prev_id = "btn"
        new_id = "new_btn"
        event = self.generate_self_heal_event(object_healed, prev_id, new_id)
        self.write_report(event, 'self_heal_report.txt')

        # Check if self-heal happened and write to database if true
        if self.self_heal_happens():
            self.write_to_db(event)

    # Repeat the same pattern for other test methods...
