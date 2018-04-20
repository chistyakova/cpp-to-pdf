import json
import os
import re
import sys
from enum import Enum, auto
from inspect import currentframe, getframeinfo


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


# Сохраняем найденные во всех *.cpp вызовы json_auto_generator_, вида:
# ['Trenaj_Mission(m_statistcs)', 'Violation_vector(m_violations)', 'File_Refuse(m_ref_datas)']
generators = []

'''
{
"TypeName":
    {
        "type":[own/enum/std::vector],
        "value": зависит от "type"
    }
}
'''
structs = {}

for root, dirs, files in os.walk(r'D:\svn\su30mki\branches\cpp-to-pdf'):
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
                    if line.startswith('struct '):
                        if ';' in line:
                            continue  # (это оказалось Forward declaration - пропускаем эту строку)
                        try:
                            current_struct_name = line.split()[1]  # ...запоминаем имя текущей стркутуры
                        except:
                            print('exception at line %s: split line: "%s" from file "%s"'
                                  % (getframeinfo(currentframe()).lineno, line, file_path))
                            current_struct_name = ''
                            continue

                        structs[current_struct_name] = {"type": "own", "value": []}
                    elif current_struct_name:
                        if '(' in line or '};' in line:
                            current_struct_name = ''
                        elif ';' in line:  # В line теперь определение поля струтуры
                            line = line.split(';', 1)[0].strip().replace('\t', ' ').replace('{', '')
                            splits = line.rsplit(' ', 1)
                            if len(splits) == 2:
                                structs[current_struct_name]['value'].append({"type": splits[0].strip(), "name": splits[1].strip()})
                    elif line.startswith('typedef std::vector'):
                        structs[line.split()[-1].replace(';', '')] = line.replace('typedef ', '').replace(';', '')
                    elif line.startswith('typedef st::types::byte'):
                        structs[line.split()[-1].replace(';', '')] = line.replace('typedef ', '').replace(';', '')

#print(generators)
#print(json.dumps(structs))  # Удобно смотреть в https://jsoneditoronline.org/


def recurse_into(depth, field_type, field_name):
    tab = '\t' * depth

    # Сперва проверям тип на пренадлежность к стандартным
    if field_type == 'unsigned int':
        print(tab+'('+field_type+')'+field_name)
    elif field_type == 'int':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'std::string':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'QString':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'unsigned long':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'char':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'unsigned char':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'float':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type == 'bool':
        print(tab + '(' + field_type + ')' + field_name)
    elif field_type.startswith('std::vector'):
        print(tab + '[')
        recurse_into(depth, field_type[field_type.find('<')+1:field_type.find('>')].strip(), field_name)
        print(tab + ']')
    elif field_type in structs:
        if not type(structs[field_type]) == str:
            #print(tab+'['+field_type+']'+field_name)
            for v in structs[field_type]['value']:
                #child_type = param.rsplit(' ', 1)[0].strip()
                #child_name = param.rsplit(' ', 1)[1].strip()
                recurse_into(depth+1, v['type'], v['name'])
        else:
            print(tab + '!!! ' + field_type + ' ' + structs[field_type])
    else:
        print('*** Не найдено привило для переменной "%s" типа "%s"' % (field_name, field_type))


for generator in generators:
    print('--- генератор для: %s' % generator)
    field_type = generator.split('(')[0]
    field_name = generator.split('(')[1].replace(')','')
    recurse_into(0, field_type, field_name)
