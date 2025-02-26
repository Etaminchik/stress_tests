from variables import *
import psycopg2
from datetime import datetime
from classes import Selects
import xlsxwriter

count_tasks = int(tasks_day) + int(tasks_month) + int(tasks_3month) + int(tasks_6month) + int(tasks_year)

if tasks_http_mask == 'True': count_tasks += 8
if tasks_ip == 'True': count_tasks += 9


task_create_date = datetime.today()


con = psycopg2.connect(
  database=db, 
  user=user, 
  password=passwd, 
  host=host, 
  port=port
)
cur = con.cursor()  

p = Selects(cur, count_tasks,task_create_date,limit_logins_generic_history)
operator = p.get_operator()
print('Оператор: ', operator)



tr = {ord(a):ord(b) for a, b in zip(*symbols)}
operator_tr = operator.translate(tr)
workbook_name = str(operator_tr) + '_' + str(task_create_date.strftime("%d.%m.%y")) + '_LT.xlsx' 
workbook = xlsxwriter.Workbook(workbook_name)
worksheet = workbook.add_worksheet('TESTS')

worksheet.write(1, 0, 'Содержание проверки')
worksheet.write(1, 1, 'Диапазон поиска')
worksheet.write(1, 2, 'Норматив выполнения')

worksheet.write(1, 3, 'Время выполнения')
worksheet.write(1, 4, 'Размер результата')

num_tests = p.get_nums_tests()
for i in range(len(num_tests)):
  worksheet.write(0, 3+i*4, str(num_tests[i][1]))

def fill_http(count_tests):
  type_tests = 'http'

  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)

    if len(result) == 8:
      for j in range(2,10):
        
        worksheet.write( j, 3 + c*2,str(result[j-2][0]))
        worksheet.write( j, 4 + c*2,str(result[j-2][1]))

  worksheet.write( 2, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 2, 1, '365 дней.')
  worksheet.write( 3, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 3, 1, '365 дней.')
  worksheet.write( 4, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 4, 1, '30 дней.')
  worksheet.write( 5, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 5, 1, '30 дней.')
  worksheet.write( 6, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 6, 1, '30 дней.')
  worksheet.write( 7, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 7, 1, '1 день.')
  worksheet.write( 8, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 8, 1, '1 день.')
  worksheet.write( 9, 0, 'Поиск соединений по HTTP-URL с применением символов маскирования *.')
  worksheet.write( 9, 1, '30 дней.')


def fill_ip(count_tests):
  type_tests = 'ip'

  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    if len(result) == 9:
      for j in range(10,19):
        worksheet.write( j, 3 + c*2,str(result[j-10][0]))
        worksheet.write( j, 4 + c*2,str(result[j-10][1]))
  worksheet.write( 10, 0, 'Поиск ААА-соединений по IP-адресу пользователя.')
  worksheet.write( 10, 1, '1 день.')
  worksheet.write( 10, 2, '0:01:00')
  worksheet.write( 11, 0, 'Поиск НТТР-соединений по одиночному IP-адресу клиента.')
  worksheet.write( 11, 1, '1 день.')
  worksheet.write( 11, 2, '0:01:00')
  worksheet.write( 12, 0, 'Поиск email-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 12, 1, '1 день.')
  worksheet.write( 12, 2, '0:01:00')
  worksheet.write( 13, 0, 'Поиск im-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 13, 1, '1 день.')
  worksheet.write( 13, 2, '0:01:00')
  worksheet.write( 14, 0, 'Поиск voip-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 14, 1, '1 день.')
  worksheet.write( 14, 2, '0:01:00')
  worksheet.write( 15, 0, 'Поиск ftp-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 15, 1, '1 день.')
  worksheet.write( 15, 2, '0:01:00')
  worksheet.write( 16, 0, 'Поиск terminal-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 16, 1, '1 день.')
  worksheet.write( 16, 2, '0:01:00')
  worksheet.write( 17, 0, 'Поиск недекодированных соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 17, 1, '1 день.')
  worksheet.write( 17, 2, '0:01:00')
  worksheet.write( 18, 0, 'Поиск NAT соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
  worksheet.write( 18, 1, '1 день.')
  worksheet.write( 18, 2, '0:01:00')

def fill_raw(count_tests):

  start_c = 19

  type_tests = 'raw_001'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    count_max_current = count_max if count_max == len(result) else len(result)
    for j in range(start_c, count_max_current+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '1 день.')
      worksheet.write( j, 2, '0:01:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
      worksheet.write( j, 5 + c*2,str(result[j-start_c][2]))
      worksheet.write( j, 6 + c*2,str(result[j-start_c][3]))

  if count_max != None:start_c +=count_max

  type_tests = 'raw_030'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    count_max_current = count_max if count_max == len(result) else len(result)
    for j in range(start_c, count_max_current+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '30 дней.')
      worksheet.write( j, 2, '0:10:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
      worksheet.write( j, 5 + c*2,str(result[j-start_c][2]))
      worksheet.write( j, 6 + c*2,str(result[j-start_c][3]))
  if count_max != None:start_c +=count_max

  type_tests = 'raw_090'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    count_max_current = count_max if count_max == len(result) else len(result)
    for j in range(start_c, count_max_current+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '90 дней.')
      worksheet.write( j, 2, '0:15:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
      worksheet.write( j, 5 + c*2,str(result[j-start_c][2]))
      worksheet.write( j, 6 + c*2,str(result[j-start_c][3]))
  if count_max != None:start_c +=count_max

  type_tests = 'raw_180'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    count_max_current = count_max if count_max == len(result) else len(result)
    for j in range(start_c, count_max_current+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '180 дней.')
      worksheet.write( j, 2, '0:15:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
      worksheet.write( j, 5 + c*2,str(result[j-start_c][2]))
      worksheet.write( j, 6 + c*2,str(result[j-start_c][3]))
  if count_max != None:start_c +=count_max


fill_http(len(num_tests))
fill_ip(len(num_tests))
fill_raw(len(num_tests))


workbook.close()


con.close() 
