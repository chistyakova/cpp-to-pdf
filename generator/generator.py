import os
import re


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


generators = []
structs = {}
vectors = {}


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
                current_struct = ''
                for line in lines:
                    if line.startswith('struct'):
                        if ';' in line:
                            continue  # Пропускаем объявление класса class IntegralForm;
                        current_struct = line.split()[1]
                        structs[current_struct] = []
                    if ';' in line and '(' not in line and ')' not in line and '}' not in line and current_struct:
                        line = line.split(';', 1)[0]
                        structs[current_struct].append(line)

for generator in generators:
    struct_name = generator.split('(')[0]
    if struct_name not in structs:
        print('Не найдена стуктура %s' % struct_name)
    print(structs[struct_name])
