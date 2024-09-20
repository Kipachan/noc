import subprocess
import time
import re
import signal
import os
from check_dir import check_dir
from config import filter_expression, interface, dump, dump_parse, tmp
from check_user import check_user

# Проверка, что текущий пользователь - root:
check_user()

# Проверка существования директории с временными файлами:
check_dir(tmp)


# Запуск tcpdump:
def run_tcpdump():
    subprocess.Popen(f"/usr/sbin/tcpdump -i {interface} -l {filter_expression} > {dump} 2>/home/KVDrynkin/scripts/Network_output_checker/temp/tcpdump_error.log", shell=True)


# Функция извлечения доменных имен из дамп-файла:
def extract_domain(record):
    splits = record.strip().split(" ")
    if len(splits) < 8:
        return None
    # Включает IPv4(A?) и IPv6(AAAA?) записи доменных имен:
    if 'A?' in splits or 'AAAA?' in splits:
        return splits[7].rsplit(".", 1)[0]
    # Исключает обратные (PTR?) записи (потому что, это IP):
    elif 'PTR?' in splits:
        return None
    else:
        return splits[4].rsplit(".", 1)[0]


# Функция проверки существующих имен и запись их в переменную:
def check_existing():
    existing_domains = set()
    if os.path.exists(dump_parse):
        with open(dump_parse, 'r') as output_file:
            for line in output_file:
                domain = line.strip()
                if domain:
                    existing_domains.add(domain)
    return existing_domains


# Запуск парсера
def run_parser():
    table = set()
    with open(dump, 'r') as source:
        for line in source:
            domain = extract_domain(line)
            if domain and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain) is None:
                table.add(domain)

    # Проверка списка существующих доменных имен:
    existing_domains = check_existing()
    # Добавление в список новых доменных имен
    with open(dump_parse, 'a') as output_file:
        for domain in table:
            if domain not in existing_domains:
                output_file.write(domain + '\n')


# Функция завершающая текущий процесс tcpdump
def kill_tcpdump():
    try:
    	tcpdump_pids = subprocess.check_output(['pidof', 'tcpdump']).split()
    	for pid in tcpdump_pids:
        	print("[+] Killing PID: " + str(pid))
        	os.kill(int(pid), signal.SIGKILL)
    except subprocess.CalledProcessError:
    	print("tcpdump process not found. It might have already benn terminated.")


# Основной цикл работы модуля
while True:
    try:
    	# Захват сетевого дампа
    	run_tcpdump()
    	# Пауза (секунды)
    	time.sleep(10)
    	# Завершение процесса tcpdump
    	kill_tcpdump()
    	# Пауза (секунды)
    	time.sleep(1)
    	# Парсинг сетевого дампа
    	run_parser()
    	# Пауза (секунды)
    	time.sleep(3)
    except Exception as e:
    	print(f"An error occurred: {e}. Restarting the process...")
    	
