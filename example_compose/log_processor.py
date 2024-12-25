import subprocess
import sqlite3
import json
from datetime import datetime

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
            
            # Include all additional keys in custom_fields
            known_keys = {'timestamp', 'service', 'log_level', 'message', 'correlation_id', 'caller_module', 'caller_function', 'function_kwargs', 'custom_fields', 'event', 'level'}
            function_kwargs = log_data.get('function_kwargs', {})
            for key, value in log_data.items():
                if key not in known_keys and key not in function_kwargs:
                    log_data['custom_fields'][key] = value
            
            # Set function_kwargs separately
            log_data['function_kwargs'] = function_kwargs
            
            store_structured_log(log_data)
        else:
            store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})
    except json.JSONDecodeError:
        store_unstructured_log({'timestamp': datetime.utcnow().isoformat(), 'source': source, 'log': log})

def tail_logs():
    last_processed_timestamp = get_last_processed_timestamp()
    since_option = f"--since={last_processed_timestamp}" if last_processed_timestamp else ""
    command = f"docker-compose logs -f {since_option}"
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            process_log(output.decode('utf-8').strip(), 'docker-compose')
    
    update_last_processed_timestamp(datetime.utcnow().isoformat())

if __name__ == '__main__':
    tail_logs()