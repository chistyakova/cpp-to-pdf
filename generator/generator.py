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
                    # Пропускаем...
                    if any(x in line for x in ['return ']):
                        continue  # ...строки содержащие подстроки
                    if not line.strip():
                        continue  # ...пустые строки
                    if line.startswith(r'//'):
                        continue  # ...строки-комментарии

                    # Попали в начало опеределения новой структуры...
                    if line.startswith('struct'):
                        if ';' in line:
                            continue  # (это оказалось Forward declaration - пропускаем эту строку)
                        current_struct_name = line.split()[1]  # ...запоминаем имя текущей стркутуры
                        structs[current_struct_name] = []
                    elif current_struct_name:
                        if '(' in line or '};' in line:
                            current_struct_name = ''
                        elif ';' in line:  # В line теперь определение поля струтуры
                            line = line.split(';', 1)[0].strip().replace('\t', ' ')
                            structs[current_struct_name].append(line)
                    elif line.startswith('typedef std::vector'):
                        structs[line.split()[-1].replace(';', '')] = line.replace('typedef ', '').replace(';', '')
                        #line[line.find('<')+1:line.find('>')].strip()


def recurse_into(struct_name):
    global depth
    depth += 1
    if struct_name not in structs:
        print('*** Не найдена стуктура %s' % struct_name)
    tab = ' ' * depth
    if not type(structs[struct_name]) == str:  # Нестандартный тип
        print(tab + struct_name)
        for param in structs[struct_name]:
            splits = param.rsplit(' ', 1)
            param_name = splits[1]
            param_type = splits[0]
            print(tab*2 + param_type + ' ' + param_name)
    else:  # Стандартный тип
        print(tab + struct_name+' '+structs[struct_name])


for generator in generators:
    depth = 0
    print('---')
    recurse_into(generator.split('(')[0])
