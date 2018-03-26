# File_Refuse из D:\svn\su30mki\branches\develop\src\include\models\model-xml.h
# Normativ и Trenaj_Mission из D:\svn\su30mki\branches\develop\src\include\training_statistics.h
# Violation_vector из D:\svn\su30mki\branches\develop\src\include\rle.h

import os
import re
import sys


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


for root, dirs, files in os.walk(r'D:\svn\su30mki\branches\develop\src'):
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
sys.exit(1)
for root, dirs, files in os.walk(r'D:\tmp\gen\src\include'):
    for name in files:
        if name.endswith('.h') or name.endswith('.hpp'):
            header_file = os.path.join(root, name)
            try:
                header_file_contents = open(header_file, encoding='cp1251').read()
            except:
                try:
                    header_file_contents = open(header_file).read()
                except:
                    header_file_contents = ''
                    print('пропускаем %s' % header_file)
            if header_file_contents:
                try:
                    cppHeader = CppHeaderParser.CppHeader(header_file_contents, argType='string')
                except CppHeaderParser.CppParseError as e:
                    print(e)
                except:
                    print('пропускаем 2 %s' % header_file)
sys.exit(1)
for root, dirs, files in os.walk(r'D:\tmp\gen\src\rmi'):
    for name in files:
        if name.endswith('.cpp'):
            source_file = os.path.join(root, name)
            with open(source_file, errors='ignore') as f:
                for line in f.readlines():
                    if 'auto_generator_json_from_' in line:
                        print('Найдено использование в %s' % source_file)
                        found = re.findall('std::string json = auto_generator_json_from_(.*?)\((.*?)\);', line, re.DOTALL)
                        argument_type = found[0][0]
                        argument_name = found[0][1]
                        print(argument_type, argument_name)


sys.exit(1)



try:
    cppHeader = CppHeaderParser.CppHeader(r'D:\svn\su30mki\branches\develop\src\include\training_statistics.h')
except CppHeaderParser.CppParseError as e:
    print(e)
    sys.exit(1)

print('std::string c_to_json_auto_generator(const Trenaj_Mission &o) {')
print('    std::string r="\'Trenaj_Mission\':{";')
for property in cppHeader.classes['Trenaj_Mission']['properties']['public']:
    if (property['type'] == 'unsigned int'
            or property['type'] == 'unsigned long'):
        print('    r+="\''+property['name']+'\':"+std::to_string(o)+",";')
    else:
        print('    OWN TYPE: '+property['type'])
print('    r+="}";')
print('return r;')
print('}')