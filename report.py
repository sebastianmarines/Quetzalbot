import datetime
import csv
import random
import time
import sqlite3

def write_report(data, filename):
    with open(filename, 'a') as f:
        for key, value in data.items():
            f.write(f'{key}: {value}\n')
        f.write('\n')

def generate_self_heal_event():
    return {
        'time': datetime.datetime.now().isoformat(),
        'reason': 'Example reason',
    }

def self_heal_happens():
    return random.choice([True, False])

def write_to_db(data):
    conn = sqlite3.connect('self_heal_report.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS self_heal (time text, reason text)")
    c.execute("INSERT INTO self_heal VALUES (?, ?)", (data['time'], data['reason']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    while True:
        if self_heal_happens():
            event = generate_self_heal_event()
            write_report(event, 'self_heal_report.txt')
        time.sleep(1)