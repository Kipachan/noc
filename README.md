# Network output checker (noc)

Данный комплект python-скриптов предназначен для формирования списка уникальных DNS-имен на которые отправляет запросы локальный хост (с использованием tcpdump). Затем полученный список сопоставляется с журналом auditd, который настроен на аудит сетевых системных вызовов. Результатом сопоставления является xml в который фиксируется информация о совершенных запросах.
> Внимание! Эти скрипты не будут работать из под контейнеров. Нужно запускать либо в bare metal либо на виртуалке.

> Внимание 2! Работа скриптов протестирована только на Debian-like системах. При разворачивании на иных семействах необходимо внести корректировки.

## Описание модулей:
### config.py

Этот модуль используется для настройки всех скриптов. Представляет собой набор переменных. Все переменные хранятся здесь.

### tcpdump_parser.py

Данный модуль реализует захват трафика, его парсинг и запись результата в текстовый файл в виде списка.

### auditd_parser.py

Модуль открывает список DNS-имен, который сформировал tcpdump_parser.py и используя функцию разрешения dns-имен в ip-адреса (модуль net_dict.py) формирует словарь {ip:dns}.
Затем на основе полученного словаря, скрипт осуществляет парсинг журнала auditd и формирует массив событий. Полученный массив сохраняется в XML файл (create_xml.py).

### auditd_events_xml_parser.py

Этот модуль парсит xml файлы созданные в резульатте работы auditd_parser.py и формирует xml файл из уникальных событий. Он нужен если скопилось несколько xml файлов и появилась необходимость объеденить их в один файл и исключить неуникальные события. Для работы требует актуализированный файл c dns именами (в качестве данных для этого файла можно брать результаты tcpdump_parser.py и выбирать нужные имена, если есть необходимость включить в финальный отчет только конкретные имена, а не все что собрал tcpdump_parser.py).   

### archive.py

Модуль архивирует xml файлы в *.tar.xz архив.

### check_dir.py

Проверяет существование каталогов. Используется модулями: tcpdump_parser.py, auditd_parser.py, auditd_events_xml_parser.py

### check_user.py

Проверяет от какого имени пользователя запускается модуль tcp_dump_parser.py (должен запускаться от root).

### create_xml.py

Создает xml файл используя библиотеку xml.etree.ElementTree. используется модулем auditd_parser.py.

### net_dict.py

Модуль применяется для разрешения dns-имен в ip-адреса с помощью утилиты getent. Используется модулем auditd_parser.py.

### permission_list.py

Модуль представляющий белый\черный списки dns-имен. По-умолчанию применяется черный список (decline). Используется модулем net_dict.py. 
Черный список - decline применяется для исключения (по каким-либо причинам) DNS-имен из списка сформированного модулем tcpdump_parser.py.  
Белый список - permit применяется для использования в net_dict.py только определенных dns-имен. Напрмиер если необходимо получить информацию только по одному конкретному dns-имени.

## Расширенные модули (каталог extend)

Данные модули никак не зависят от основного блока скриптов описанных выше и нужны для работы с результатми. 

### lsx.py

Применяется для того чтобы разбить один xml файл на несколько. В зависимостей от необходимостей в модуле можно указать максимальное кол-во элементов (строк) в новых xml файлах.
Может быть полезным если например auditd_events_xml_parser.py сформировал слишком большой xml (например 1Гб) и работа с ним весьма затруднительна, то lsx.py разделит его на необходимое кол-во файлов поменьше.

## Вспомогательные файлы (каталог files)

### audit.rules

Здесь описаны правила аудита для auditd, которые фиксируют системные вызовы связанные с сетью.

### root

Это файл расписания crontab для root.

# Как с этим работать:

## Установка

Просто копируем все файлы в какой-либо каталог. Например в /project/noc. Получаем следующую структуру каталогов:
```
.
├── archive.py
├── auditd_events_xml_parser.py
├── auditd_parser.py
├── check_dir.py
├── check_user.py
├── config.py
├── create_xml.py
├── extend
│   └── lsx.py
├── files
│   ├── audit.rules
│   └── root
├── net_dict.py
├── permission_list.py
└── tcpdump_parser.py
```

## Установка дополнительных компонентов

1. Необходимо убедиться что в системе установлен auditd и tcpdump.
2. Затем нужно подложить файл audit.rules:
```
cp /project/noc/files/audit.rules /etc/audit/rules.d/
```
В каталоге rules.d может находится несколько других файлов *.rules, содержащие преднастроенные правила или как-либо иные кастомные правила. Если они не нужны - рекомендуется их удалить или переименовать в *._rules. 
> Дело в том, что чем больше правил, тем быстрее заполняются журналы. 

Чтобы auditd принял новые правила, необходимо перезагрузить сервис:
```
sudo systemctl restart auditd
```
Проверим список активных правил:
```
sudo auditctl -l

-a always,exit -F arch=b64 -S bind,connect,accept,listen -F key=net
-a always,exit -F arch=b32 -S bind,connect,listen -F key=net
```

3. Настроим конфигурационный файл auditd:
Из основного:
размер лог файла (1500 мегабайт) - max_log_file = 1500
количество лог файлов (5 штук) - num_logs = 5
действие при достижении максимального размера лог файла (перемещать) - max_log_file_action = ROTATE

Итого, логи пишутся в файл, максимальный размер которого может быть 1500 мегабайт, в случае достижения этого размера, создается следующий файл. Если количество файлов достигает 5 штук, они начинают по очереди перезаписываться. Эти настройки можно поменять при необходимости.
```
nano /etc/audit/auditd.conf

#
# This file controls the configuration of the audit daemon
#

local_events = yes
write_logs = yes
log_file = /var/log/audit/audit.log
log_group = adm
log_format = ENRICHED
flush = INCREMENTAL_ASYNC
freq = 50
max_log_file = 1500
num_logs = 5
priority_boost = 4
name_format = NONE
##name = mydomain
max_log_file_action = ROTATE
space_left = 75
space_left_action = SYSLOG
verify_email = yes
action_mail_acct = root
admin_space_left = 50
admin_space_left_action = SUSPEND
disk_full_action = SUSPEND
disk_error_action = SUSPEND
use_libwrap = yes
##tcp_listen_port = 60
tcp_listen_queue = 5
tcp_max_per_addr = 1
##tcp_client_ports = 1024-65535
tcp_client_max_idle = 0
transport = TCP
krb5_principal = auditd
##krb5_key_file = /etc/audit/audit.key
distribute_network = no
q_depth = 400
overflow_action = SYSLOG
max_restarts = 10
plugin_dir = /etc/audit/plugins.d
```
4. Настроим crontab, чтобы noc работал в автоматическом режиме.
```
cp /project/noc/files/root  /var/spool/cron/crontabs/
```
Рассмотрим подробнее что там происходит:

```
sudo crontab -l
```
Получим текущее расписание. 

```
# DO NOT EDIT THIS FILE - edit the master and reinstall.
# (/tmp/crontab.sJRYzk/crontab installed on Thu Jun 13 15:01:32 2024)
# (Cron version -- $Id: crontab.c,v 2.13 1994/01/17 03:20:37 vixie Exp $)
# Edit this file to introduce tasks to be run by cron.
# 
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
# 
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
# 
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
# 
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).
# 
# For example, you can run a backup of all your user accounts
# at 5 a.m every week with:
# 0 5 * * 1 tar -zcf /var/backups/home.tgz /home/
# 
# For more information see the manual pages of crontab(5) and cron(8)
# 
# m h  dom mon dow   command
#
#
#
#
#
#>>> Network_output_checker <<<
#
#start evening tcpdump proccess
0 18 * * * nohup /usr/bin/python3 /project/noc/tcpdump_parser.py > /project/noc/temp/tcpdump_parser.log 2>&1 &
#
#kill scripts proccess:
0 17 * * * pkill -f tcpdump_parser.py
#
#kill tcpdump proccess:
0 17 * * * pkill -f tcpdump
#
#make evening auditd events report:
1 17 * * * nohup /usr/bin/python3 /project/noc/auditd_parser.py > /project/noc/temp/auditd_parser.log 2>&1 &
#
#start night tcpdump proccess
0 3 * * * nohup /usr/bin/python3 /project/noc/tcpdump_parser.py > /project/noc/temp/tcpdump_parser.log 2>&1 &
#
#kill scripts proccess:
0 2 * * * pkill -f tcpdump_parser.py
#
#kill tcpdump proccess:
0 2 * * * pkill -f tcpdump
#
#make night auditd events report:
1 2 * * * nohup /usr/bin/python3 /project/noc/auditd_parser.py > /project/noc/temp/auditd_parser.log 2>&1 &
#
#Archiving XML parsed auditd logs
0 3 * * 1 nohup /usr/bin/python3 /project/noc/archive.py 
```
Логика следующая:
1. Каждый день в 02:00 cron убивает запущенный ранее процесс захвата и парсинга трафика (для исключения коллизий)
```
#kill scripts proccess:
0 2 * * * pkill -f tcpdump_parser.py
#
#kill tcpdump proccess:
0 2 * * * pkill -f tcpdump
```
2. Затем cron запускает процесс парсинга журналов аудита.
```
#make night auditd events report:
1 2 * * * nohup /usr/bin/python3 /project/noc/auditd_parser.py > /project/noc/temp/auditd_parser.log 2>&1 &
```
3. В 03:00 cron возобновляет работу tcpdump_parser.py
```
#
#start night tcpdump proccess
0 3 * * * nohup /usr/bin/python3 /project/noc/tcpdump_parser.py > /project/noc/temp/tcpdump_parser.log 2>&1 &
#
```
4. Далее cron повторяет операцию из пункта 1,  но уже вечером
```
#kill scripts proccess:
0 17 * * * pkill -f tcpdump_parser.py
#
#kill tcpdump proccess:
0 17 * * * pkill -f tcpdump
#
```
5. То же самое что и в пунтке 2 только вечером
```
#make evening auditd events report:
1 17 * * * nohup /usr/bin/python3 /project/noc/auditd_parser.py > /project/noc/temp/auditd_parser.log 2>&1 &
#
```
6. То же что и в пункте 3 только вечером
```
#start evening tcpdump proccess
0 18 * * * nohup /usr/bin/python3 /project/noc/tcpdump_parser.py > /project/noc/temp/tcpdump_parser.log 2>&1 &
#
```
7. По понедельникам cron запускает скрипт archive.py, который архивирует (tar.xz) xml файлы.
```
#Archiving XML parsed auditd logs
0 3 * * 1 nohup /usr/bin/python3 /project/noc/archive.py 
```

> Подытожим: cутки напролет tcpdump анализирует и парсит трафик. Два раза в сутки на основе этого парсинга формируются xml отчеты. Раз в неделю эти отчеты архивируются и сжимаются.

## Настройка файла конфигурации noc (config.py)

Данный файл представляет собой хранилище переменных используемых noc.
```

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
```
