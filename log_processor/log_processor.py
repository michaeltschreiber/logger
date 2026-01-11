import json
import os
import sqlite3
import subprocess
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

STRUCTURED_LOG_COLUMNS = [
    ("timestamp", "TEXT"),
    ("service", "TEXT"),
    ("log_level", "TEXT"),
    ("message", "TEXT"),
    ("correlation_id", "TEXT"),
    ("filename", "TEXT"),
    ("func_name", "TEXT"),
    ("lineno", "INTEGER"),
    ("request_id", "TEXT"),
    ("user_id", "TEXT"),
    ("custom_fields", "TEXT"),
]

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS structured_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    service TEXT,
    log_level TEXT,
    message TEXT,
    correlation_id TEXT,
    filename TEXT,
    func_name TEXT,
    lineno INTEGER,
    request_id TEXT,
    user_id TEXT,
    custom_fields TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS unstructured_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    source TEXT,
    log TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS timestamp (
    id INTEGER PRIMARY KEY,
    last_processed TIMESTAMP
)
''')

conn.commit()

def ensure_structured_log_columns():
    cursor.execute('PRAGMA table_info(structured_logs)')
    existing = {row[1] for row in cursor.fetchall()}
    for name, col_type in STRUCTURED_LOG_COLUMNS:
        if name not in existing:
            cursor.execute(f'ALTER TABLE structured_logs ADD COLUMN {name} {col_type}')
    conn.commit()

ensure_structured_log_columns()

def get_last_processed_timestamp():
    cursor.execute('SELECT last_processed FROM timestamp WHERE id=1')
    row = cursor.fetchone()
    return row[0] if row else None

def update_last_processed_timestamp(timestamp):
    cursor.execute('INSERT OR REPLACE INTO timestamp (id, last_processed) VALUES (?, ?)', (1, timestamp))
    conn.commit()

def store_structured_log(log):
    cursor.execute('''
    INSERT INTO structured_logs (timestamp, service, log_level, message, correlation_id, filename, func_name, lineno, request_id, user_id, custom_fields)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        log.get('timestamp', ''),
        log.get('service', ''),
        log.get('log_level', ''),
        log.get('message', ''),
        log.get('correlation_id', ''),
        log.get('filename', ''),
        log.get('func_name', ''),
        log.get('lineno', None),
        log.get('request_id', ''),
        log.get('user_id', ''),
        json.dumps(log.get('custom_fields', {}))
    ))
    conn.commit()

def store_unstructured_log(log):
    cursor.execute('''
    INSERT INTO unstructured_logs (timestamp, source, log)
    VALUES (?, ?, ?)
    ''', (
        log['timestamp'],
        log['source'],
        log['log']
    ))
    conn.commit()

def process_log(log, source):
    try:
        # Extract the service name and JSON part of the log
        if ' | ' in log:
            service, log = log.split(' | ', 1)
        else:
            service = source
        
        log_data = json.loads(log)
        if 'event' in log_data and 'level' in log_data:
            log_data['timestamp'] = datetime.utcnow().isoformat()
            log_data['service'] = service.strip()
            log_data['log_level'] = log_data['level']
            log_data['message'] = log_data['event']
            log_data['custom_fields'] = log_data.get('custom_fields', {})
            if 'function_kwargs' in log_data:
                log_data['custom_fields']['function_kwargs'] = log_data['function_kwargs']

            # Include all additional keys in custom_fields
            known_keys = {
                'timestamp',
                'service',
                'log_level',
                'message',
                'correlation_id',
                'filename',
                'func_name',
                'lineno',
                'request_id',
                'user_id',
                'custom_fields',
                'event',
                'level',
                'function_kwargs',
            }
            for key, value in log_data.items():
                if key not in known_keys:
                    log_data['custom_fields'][key] = value
            
            store_structured_log(log_data)
        else:
            store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})
    except json.JSONDecodeError:
        store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})

def tail_logs():
    last_processed_timestamp = get_last_processed_timestamp()
    repo_root = os.path.dirname(os.path.abspath(__file__))
    compose_file = os.path.normpath(os.path.join(repo_root, '..', 'example_compose', 'docker-compose.yml'))
    command = ["docker", "compose", "-f", compose_file, "logs", "-f"]
    if last_processed_timestamp:
        command.extend(["--since", last_processed_timestamp])

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break

            if output:
                new_timestamp = datetime.utcnow().isoformat()
                try:
                    process_log(output.decode('utf-8').strip(), 'docker-compose')
                    update_last_processed_timestamp(new_timestamp)
                except Exception as e:
                    print(f"Error processing log: {e}")
    finally:
        if process:
            process.terminate()

if __name__ == '__main__':
    tail_logs()
