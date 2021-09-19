# pip install elasticsearch
# pip install psutil

import psutil
import time
from elasticsearch import Elasticsearch, helpers
from datetime import datetime, timedelta

ELASTICSEARCH_URL = "http://elasticsearch:9200/"

# Wait for elasticsearch and kibana service to run
time.sleep(50)

es = Elasticsearch(timeout = 600, hosts = ELASTICSEARCH_URL)
print(es.ping())

def get_processes_info():
    processes = []
    for process in psutil.process_iter():
        with process.oneshot():
            
            pid = process.pid
            if pid == 0:
                continue
            name = process.name()

            # Try to get the time when the process was started if error occurs then assign the time as to when the system was started
            try:
                create_time = datetime.fromtimestamp(process.create_time())
            except OSError:
                create_time = datetime.fromtimestamp(psutil.boot_time())
            
            # Get the CPU usage, process status and memory percent of the process
            cpu_usage = process.cpu_percent()
            status = process.status()
            memory_usage = process.memory_percent()

            try:
                username = process.username()
            except psutil.AccessDenied:
                username = "N/A"
            
        processes.append({
            'pid': pid, 
            'name': name, 
            'username': username,
            'cpu_usage': cpu_usage, 
            'status': status, 
            'memory_usage': memory_usage, 
            'created_on': create_time
        })

        # Sort the process in increasing order of cpu usage and memory usage
        processes = sorted(processes, key=lambda procObj: (procObj['cpu_usage'],procObj['memory_usage']), reverse=True)

    return processes

def data_generator(processes):
    data = []
    now = datetime.now()
    for p in processes:
        temp_data = {
            '_index': 'system-process',
            '_source': {
                'pid': p['pid'],
                'name': p['name'], 
                'username': p['username'],
                'cpu_usage': p['cpu_usage'], 
                'status': p['status'], 
                'memory_usage': p['memory_usage'],
                'created_on': p['created_on'],
                'current_time': now
            }
        }
        data.append(temp_data)
    return data

current_time = datetime.now()
run_till_time = current_time + timedelta(minutes = 10)

while datetime.now() <= run_till_time:
    processes = get_processes_info()
    process_data = data_generator(processes)
    res = helpers.bulk(es, process_data)
    time.sleep(1)




