import xml.etree.ElementTree as ET
import os


def write_to_xml(events_data, xml_file):
	root = ET.Element("audit_events")
	# Пройти по всем данным о событиях и создать для каждого элемент XML
	for event_data in events_data:
		event = ET.SubElement(root, "event")
		for key, value in event_data.items():
			ET.SubElement(event, key).text = value

	# Функция для генерации нового имени файла, если он уже существует
	def generate_new_filename(file_path):
		base, extension = os.path.splitext(file_path)
		i = 1
		new_file_path = f"{base}_({i}){extension}"
		while os.path.exists(new_file_path):
			i += 1
			new_file_path = f"{base}_({i}){extension}"

		return new_file_path

	# Проверка на существование файла и генерация нового имени при необходимости
	if os.path.exists(xml_file):
		xml_file = generate_new_filename(xml_file) 

	# Записать все изменения в XML-файл одним вызовом
	tree = ET.ElementTree(root)
	tree.write(xml_file)
	print(f'Завершено. Отчет сохранен в: {xml_file}')
