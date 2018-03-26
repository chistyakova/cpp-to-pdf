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
                    if any(x in line for x in ['return ', ')', '(']):
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
                        structs[current_struct_name] = (None, [])
                    elif current_struct_name != '':
                        if ';' in line and len(line.split()) > 1:  # В line теперь определение поля струтуры
                            print('--------' + current_struct_name)
                            line = line.split(';', 1)[0].strip()

                            structs[current_struct_name][1].append(line)
                        elif '(' in line:
                            print('!!!!!!!!!'+current_struct_name)
                            current_struct_name = ''
                    if line.startswith('typedef std::vector'):
                        print('****** '+current_struct_name+' '+line)
                        structs[line.split()[-1].replace(';', '')] = ('std::vector', line[line.find('<')+1:line.find('>')].strip())


def recurse_into(struct_name):
    global depth
    depth += 1
    if struct_name not in structs:
        print('*** Не найдена стуктура %s' % struct_name)
    tab = '-' * depth
    print(tab + struct_name)
    if not structs[struct_name][0]:  # Нестандартный тип
        for param in structs[struct_name][1]:
            print(tab+param)
    else:  # Стандартный тип
        print('standard')


for generator in generators:
    depth = 0
    recurse_into(generator.split('(')[0])
