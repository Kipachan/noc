from net_dict import getent_dict
from config import dump_parse, xml_dir, xml_file
from create_xml import write_to_xml
from check_dir import check_dir
import subprocess
import re

check_dir(xml_dir)

def process_event_data(ip, dns, event):
    event_date = re.search(r'(\d{2}\.\d{2}\.\d{4})', event).group(1)
    event_time = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3})', event).group(1)
    event_proc_match = re.search(r'proctitle=([^\s]+)', event)
    event_proc = event_proc_match.group(1) if event_proc_match else None
    event_comm_match = re.search(r'comm=([^\s]+)', event)
    event_comm = event_comm_match.group(1) if event_comm_match else None
    event_port_match = re.search(r'lport=([^\s]+)', event)
    event_port = event_port_match.group(1) if event_port_match else None
    event_exe_match = re.search(r'exe=([^\s]+)', event)
    event_exe = event_exe_match.group(1) if event_exe_match else None
    event_uid_match = re.search(r'uid=([^\s]+)', event)
    event_uid = event_uid_match.group(1) if event_uid_match else None
    event_gid_match = re.search(r'gid=([^\s]+)', event)
    event_gid = event_gid_match.group(1) if event_gid_match else None
    event_success_match = re.search(r'success=([^\s]+)', event)
    event_success = event_success_match.group(1) if event_success_match else None
    event_exit_match = re.search(r'exit=(.*?)\sa0=', event)
    event_exit = event_exit_match.group(1) if event_exit_match else None

    return {
        'event_date': event_date,
        'event_time': event_time,
       	'ip': ip,
        'dns': dns,
        'event_proc': event_proc,
        'event_comm': event_comm,
        'event_port': event_port,
        'event_exe': event_exe,
        'event_uid': event_uid,
        'event_gid': event_gid,
        'event_success': event_success,
        'event_exit': event_exit
    }


# Вызываем функцию разрешения dns-имен в ip-адреса и получаем словарь, где ключом является ip-адрес,
# а значением dns-имя. Функция принимает список dns имен, который составил модуль tcpdump_parser.
print('Вызов функции разрешения dns-имен в ip-адреса \n')
connections_dict = getent_dict(dump_parse)
print('Формирование словаря завершено. \n')

# Сбор данных о событиях в массив
print('Формируем массив событий \n')
events_data = []
for ip, dns in connections_dict.items():
    stage_one = subprocess.run(f"/usr/sbin/ausearch -i -hn {ip}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8', errors='replace')
    output_stage_one = stage_one.stdout.split('----')
    for event in output_stage_one:
        if len(event) > 0:
            event_data = process_event_data(ip, dns, event)
            events_data.append(event_data)
print('Массив сформирован \n')

# Запись данных в XML после того, как все события обработаны
print('Запись данных в xml \n')
write_to_xml(events_data, xml_file)
