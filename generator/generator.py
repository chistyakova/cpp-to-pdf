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


def cpp_comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ' '
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


generators = []  # Сохраняем найденные во всех *.cpp вызовы json_auto_generator_, которые будем потом генерировать
structs = {}  # Словарь вида ИМЯ_СТРУКТУРЫ:СТРУКТУРА


for root, dirs, files in os.walk(r'D:\tmp\cpp-to-json-generator\src'):
    for name in files:
        if name.startswith('ui_'):
            continue
        file_path = os.path.join(root, name)
        if file_path.endswith('.h') or file_path.endswith('.hpp') or file_path.endswith('.cpp'):
            contents = readfile(file_path)
            # Удаляем комментарии
            contents = cpp_comment_remover(contents)

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
                            line = line.split(';', 1)[0].strip().replace('\t', ' ').replace('{', '')
                            structs[current_struct_name].append(line)
                    elif line.startswith('typedef std::vector'):
                        structs[line.split()[-1].replace(';', '')] = line.replace('typedef ', '').replace(';', '')
                    elif line.startswith('typedef st::types::byte'):
                        structs[line.split()[-1].replace(';', '')] = line.replace('typedef ', '').replace(';', '')


def recurse_into(depth, fieled_type, fieled_name):
    tab = '\t' * depth

    # Сперва проверям тип на пренадлежность к стандартным
    if fieled_type == 'unsigned int':
        print(tab+'('+fieled_type+')'+fieled_name)
    elif fieled_type == 'int':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'std::string':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'QString':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'unsigned long':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'char':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'unsigned char':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'float':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type == 'bool':
        print(tab + '(' + fieled_type + ')' + fieled_name)
    elif fieled_type.startswith('std::vector'):
        print(tab + '[')
        recurse_into(depth, fieled_type[fieled_type.find('<')+1:fieled_type.find('>')].strip(), fieled_name)
        print(tab + ']')
    elif fieled_type in structs:
        if not type(structs[fieled_type]) == str:
            print(tab+'['+fieled_type+']'+fieled_name)
            for param in structs[fieled_type]:
                child_type = param.rsplit(' ', 1)[0].strip()
                child_name = param.rsplit(' ', 1)[1].strip()
                recurse_into(depth+1, child_type, child_name)
        else:
            print(tab + fieled_type + ' ! ' + structs[fieled_type])
    else:
        print('*** Не найдено привило для переменной "%s" типа "%s"' % (fieled_name, fieled_type))


for generator in generators:
    print('---')
    fieled_type = generator.split('(')[0]
    fieled_name = generator.split('(')[1].replace(')','')
    recurse_into(0, fieled_type, fieled_name)
