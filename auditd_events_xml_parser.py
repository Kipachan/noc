import os
import xml.etree.ElementTree as ET
from check_dir import check_dir
from config import xml_dir, result_xml, src_data

check_dir(xml_dir)

def find_events_by_ips(input_dir, output_file, search_ips):
	event_tuple = ()
	#Создаем корневой элемент для результирующего XML:
	root = ET.Element("audit_events")

	#Множество для хранений уникальных событий
	unique_events = set()

	#Проходим по всем файлам в заданной директории
	for filename in os.listdir(input_dir):
		if filename.endswith(".xml"):
			file_path = os.path.join(input_dir, filename)
			tree = ET.parse(file_path)
			root_tree = tree.getroot()

			#Ищем все события с нужным IP
			for event in root_tree.findall('event'):
				ip_element = event.find('dns')
				if ip_element is not None and ip_element.text in search_ips:
					#Преобразуем событие в кортеж значений его элементов
					event_tuple = tuple(child.text for child in event)

				#Проверяем уникальные события:
				if event_tuple not in unique_events:
					unique_events.add(event_tuple)
					root.append(event)

	#Записываем результирующий XML в файл:
	tree = ET.ElementTree(root)
	tree.write(output_file, encoding='utf-8', xml_declaration=True)


#Указываем необходимые параметры парсинга:
input_directory = xml_dir #путь к директории с xml файлами
output_xml_file = result_xml #путь сохранения результирующего файла
dns_to_search = [] #список ip-адресов, по которым осуществляется поиск
with open(src_data, 'r') as src:
	dns_to_search = [line.strip() for line in src.read().strip().splitlines()]
print(f'Парсим следующие адреса: {dns_to_search}')
find_events_by_ips(input_directory, output_xml_file, dns_to_search) 

