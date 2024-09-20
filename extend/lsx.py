import xml.etree.ElementTree as ET
import os

def split_xml(input_file, output_dir, max_elements_per_file):
    # Создаем выходную директорию, если она не существует
    os.makedirs(output_dir, exist_ok=True)

    # Читаем исходный XML-файл
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Счетчик для файла и элемента
    file_counter = 1
    element_counter = 0

    # Новый корень для поддерева
    new_root = ET.Element(root.tag)

    # Проходим по всем элементам в корневом элементе
    for child in root:
        new_root.append(child)
        element_counter += 1

        # Когда достигнем максимального количества элементов, создаем новый файл
        if element_counter >= max_elements_per_file:
            # Создаем дерево и записываем его в файл
            new_tree = ET.ElementTree(new_root)
            new_tree.write(os.path.join(output_dir, f'output_{file_counter}.xml'), encoding='utf-8', xml_declaration=True)

            # Обнуляем счетчики и создаем новый корень для следующей части
            file_counter += 1
            element_counter = 0
            new_root = ET.Element(root.tag)

    # Записываем оставшиеся элементы, если есть
    if len(new_root):
        new_tree = ET.ElementTree(new_root)
        new_tree.write(os.path.join(output_dir, f'output_{file_counter}.xml'), encoding='utf-8', xml_declaration=True)

# Пример использования
input_file = 'large_file.xml'
output_dir = 'output_parts'
max_elements_per_file = 200000  # Измените это значение в зависимости от ваших требований

split_xml(input_file, output_dir, max_elements_per_file)
