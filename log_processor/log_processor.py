import docker
import sqlite3
import json
from datetime import datetime
import inspect
import sys

# Initialize Docker client
client = docker.from_env()

# Connect to SQLite database
conn = sqlite3.connect('logs.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS structured_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    service TEXT,
    log_level TEXT,
    message TEXT,
    correlation_id TEXT,
    caller_module TEXT,
    caller_function TEXT,
    function_kwargs TEXT,
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

def get_last_processed_timestamp():
    cursor.execute('SELECT last_processed FROM timestamp ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    return row[0] if row else None

def update_last_processed_timestamp(timestamp):
    cursor.execute('INSERT INTO timestamp (last_processed) VALUES (?)', (timestamp,))
    conn.commit()

def store_structured_log(log):
    cursor.execute('''
    INSERT INTO structured_logs (timestamp, service, log_level, message, correlation_id, caller_module, caller_function, function_kwargs, custom_fields)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        log['timestamp'],
        log['service'],
        log['log_level'],
        log['message'],
        log.get('correlation_id', ''),
        log.get('caller_module', ''),
        log.get('caller_function', ''),
        json.dumps(log.get('function_kwargs', {})),
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

def add_caller_info(log):
    frame = sys._getframe(3)  # Go three frames up to get the caller
    log['caller_module'] = frame.f_globals['__name__']
    log['caller_function'] = frame.f_code.co_name

    # Capture function arguments
    try:
        args, _, _, values = inspect.getargvalues(frame)
        kwargs = {arg: values[arg] for arg in args}
        log['function_kwargs'] = kwargs
    except Exception:
        log['function_kwargs'] = "Unable to extract kwargs"

    return log

def process_log(log, source):
    try:
        log_data = json.loads(log)
        if 'service' in log_data and 'log_level' in log_data and 'message' in log_data:
            log_data['timestamp'] = datetime.utcnow().isoformat()
            log_data['custom_fields'] = log_data.get('custom_fields', {})
            log_data = add_caller_info(log_data)
            store_structured_log(log_data)
        else:
            store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})
    except json.JSONDecodeError:
        store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})

def tail_logs():
    last_processed_timestamp = get_last_processed_timestamp()
    for container in client.containers.list():
        for line in container.logs(stream=True, since=last_processed_timestamp):
            process_log(line.decode('utf-8').strip(), container.name)
    update_last_processed_timestamp(datetime.utcnow().isoformat())

if __name__ == '__main__':
    tail_logs()