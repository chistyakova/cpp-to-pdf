import os
import re
import sys
from enum import Enum, auto

def readfile(file_path):
    try:
        contents = open(file_path, encoding='cp1251').read()
    except:
        try:
            contents = open(file_path, encoding='utf8').read()
        except:
            try:
                contents = open(file_path, errors='ignore').read()
            except:
                print('Ошибка чтения %s' % file_path)
                contents = ''
    return contents


generators = []  # Сохраняем найденные во всех *.cpp вызовы json_auto_generator_, которые будем потом генерировать
structs = {}  # Словарь вида ИМЯ_СТРУКТУРЫ:СТРУКТУРА


for root, dirs, files in os.walk(r'D:\tmp\cpp-to-json-generator\src'):
    for name in files:
        if name.startswith('ui_'):
            continue
        file_path = os.path.join(root, name)
        if file_path.endswith('.h') or file_path.endswith('.hpp') or file_path.endswith('.cpp'):
            contents = readfile(file_path)
            if file_path.endswith('.cpp'):
                matches = re.findall('json_auto_generator_(.*?\))', contents, re.DOTALL)
                for match in matches:
                    generators.append(match)
            if file_path.endswith('.h') or file_path.endswith('.hpp'):
                lines = contents.split('\n')
                current_struct_name = ''
                for line in lines:
                    if line.startswith('struct'):
                        if ';' in line:
                            continue  # Пропускаем объявление класса class IntegralForm;
                        current_struct_name = line.split()[1]
                        structs[current_struct_name] = {'type': 'own', 'data': []}
                    if ';' in line and '(' not in line and ')' not in line and '}' not in line and current_struct_name:
                        line = line.split(';', 1)[0]
                        structs[current_struct_name]['data'].append(line)
                    if line.startswith('typedef std::vector'):
                        structs[line.split()[-1].replace(';', '')] = {'type': 'std_vector', 'data': line[line.find('<')+1:line.find('>')].strip()}

for generator in generators:
    struct_name = generator.split('(')[0]
    if struct_name not in structs:
        print('Не найдена стуктура %s' % struct_name)
    print(structs[struct_name])
