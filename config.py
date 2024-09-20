from pathlib import Path

"""
Путь директории временных файлов:
"""
tmp = Path("/project/noc/temp")

"""
Путь директории отчетов аудита:
"""
xml_dir = Path("/project/noc/temp/xml")

"""
Настройки tcpdump
"""
# Имя сетевого интерфейса:
interface = 'bond0'

# IP-адрес источника:
ip_src = '172.16.0.19'

# Путь сохранения дамп файла tcpdump:
dump = '/project/noc/temp/tcpdump_report'

# Выражение-фильтр для условий захвата трафика tcpdump:
filter_expression = f'"(ip src host {ip_src} and not icmp and tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack = 0) or (ip src host {ip_src} and not icmp and udp)"'

"""
Настройки tcpdump_parser
"""
# Результаты парсинга дампа захваченного трафика:
dump_parse = '/project/noc/temp/tcpdump_parse'

"""
Настройки create_xml
"""
# Путь сохранения отчета аудита:
from datetime import datetime
date = datetime.now().date()
xml_file = f'/project/noc/temp/xml/audit_events_{date}.xml'

"""
Настройки audit_events_xml_parser
"""
#Результат парсинга по xml файлам с отчетами аудита
result_xml = f'/project/noc/temp/result_{date}.xml'

#Источник данных по которым производится парсинг (ip)
src_data = '/project/noc/temp/src/dns'

"""
Настройки archive
"""
# Путь сохранения архивов
archive_path = '/project/noc/temp/xml/archive'