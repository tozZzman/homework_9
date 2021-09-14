from subprocess import run, PIPE
import re
import pandas as pd
from datetime import datetime

system_info = run(['ps', 'aux'], stdout=PIPE, stderr=PIPE).stdout.decode('utf-8')
system_info = system_info.split('\n')

dict_report = {"Пользователей системы": None,
               "Процессов запущено": None,
               "Пользовательских процессов": None,
               "Всего памяти используется": None,
               "Всего CPU используется": None,
               "Больше всего памяти использует": None,
               "Больше всего CPU использует": None}
columns = []
values = []
users = []

for line in system_info:
    if system_info.index(line) == 0:
        columns.append(line)
        continue
    else:
        values.append(line)
    user = re.search(r'^\S+', line)
    if user is not None and user.group() not in users:
        users.append(user.group())

dict_report["Пользователей системы"] = ', '.join(users)
dict_report["Процессов запущено"] = len(values) - 1
columns = re.split(r'\s+', columns[0])
values = [re.split(r'\s+', val) for val in values]

for val in values:
    if len(val) < len(columns):
        continue
    if len(columns) < len(val):
        comm = ''
        for item in val[len(columns) - 1:len(val)]:
            comm = comm + ' ' + item
            val[len(columns) - 1] = comm
        values[values.index(val)] = val = val[:-(len(val) - len(columns))]
    values[values.index(val)][2] = float(values[values.index(val)][2])
    values[values.index(val)][3] = float(values[values.index(val)][3])

df = pd.DataFrame(values, columns=columns)

dict_proc_usr = dict()
for user in users:
    dict_proc_usr[user] = len(df.loc[df.USER == user].iloc[:])
    str_proc_usr = ', '.join([f'{key}: {val}' for key, val in dict_proc_usr.items()])
    dict_report["Пользовательских процессов"] = str_proc_usr

cpu_proc = df.sort_values(by=['%CPU'], ascending=False).values.tolist()
dict_report["Больше всего CPU использует"] = cpu_proc[0][10][:20] + ': ' + str(cpu_proc[0][2])

mem_proc = df.sort_values(by=['%MEM'], ascending=False).values.tolist()
dict_report["Больше всего памяти использует"] = mem_proc[0][10][:20] + ': ' + str(mem_proc[0][3])

cpu_all = df.iloc[:, 2].values.tolist()
dict_report["Всего CPU используется"] = sum(cpu_all[:-1])

mem_all = df.iloc[:, 3].values.tolist()
dict_report["Всего памяти используется"] = sum(mem_all[:-1])

dict_report = ';\n'.join([f'{key}: {val}' for key, val in dict_report.items()])
print(dict_report)

name = str(datetime.now())[:16].replace(' ', '-') + '-scan.txt'
with open(file=name, mode='w') as f:
    f.write(dict_report)
