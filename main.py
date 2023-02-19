
from variables import *
from classes import Selects
import psycopg2
from datetime import datetime, timedelta
import ipaddress
import time
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE, formatdate


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

#print(task_create_date.strftime("%Y-%m-%d %H:%M:%S"))

curent_tests = p.find_old_tests()[0][0] + 1 if p.find_old_tests() else 1
print('Текущий тест: ',curent_tests)
logins = p.get_logins()
sess_id,sess_uid = p.get_sessid()
current_login_num = 0

def create_comment(type_tests_,number_,all_):
  prefix = 'load_tests'
  number_of_tests = curent_tests
  type_tests = type_tests_
  number = number_
  all = all_
  comment = ['Comment:',prefix,str(number_of_tests).zfill(2),type_tests,str(number+1).zfill(3),str(all).zfill(3)]
  return '/'.join(comment)




def create_task_login(c,days):
  global current_login_num
  for i in range(c):
    with open(path_raw_login, 'r') as file:
      filedata = file.read()
    
    filedata = filedata.replace('[comment]', create_comment('raw_'+str(days).zfill(3),i,c))

    start_date = (datetime.today() - timedelta(days=days)).strftime("%y%m%d%H%M%S")
    end_date = datetime.today().strftime("%y%m%d%H%M%S")
    low_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")
    high_date = datetime.today().strftime("%Y-%m-%d")
    
    filedata = filedata.replace('[sess_uid]', sess_uid)
    filedata = filedata.replace('[start_date]', str(start_date))
    filedata = filedata.replace('[end_date]', str(end_date))
    filedata = filedata.replace('[abonent_id]', logins[current_login_num])
    filedata = filedata.replace('[sess_id]', str(sess_id))
    filedata = filedata.replace('[low_date]', str(low_date))
    filedata = filedata.replace('[high_date]', str(high_date))
    filedata = filedata.replace('[task_create_date]', str(task_create_date))

    cur.execute(filedata)
    con.commit() # save
    current_login_num +=1
    time.sleep(2)

  return "[ OK ] raw задачи созданы"


def create_task_abonents():
  with open(path_abonents, 'r') as file:
    filedata = file.read()
  
  logins = p.get_logins_generic_history()
  select = ''
  insert = "\n\
                  <separator>2</separator>\n\
                  <recoded-find-mask>\n\
                     <data-network-identifier>\n\
                        <login>[login]</login>\n\
                     </data-network-identifier>\n\
                  </recoded-find-mask>"
  for login in logins:
    select += insert.replace('[login]',login[0])

  filedata = filedata.replace('[sess_id]', str(sess_id))
  filedata = filedata.replace('[sess_uid]', sess_uid)
  filedata = filedata.replace('[insert_login]', select)
  filedata = filedata.replace('[task_create_date]', str(task_create_date))
  cur.execute(filedata)
  con.commit() # save
  print('Загружен таск с ', len(logins), ' абонентами.')
  return "[ OK ] abonents задачи созданы"


def create_task_http():
  global current_login_num
  low_date_year   = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
  low_date_month  = (datetime.today() - timedelta(days=30)) .strftime("%Y-%m-%d")
  low_date_day    = (datetime.today() - timedelta(days=1))  .strftime("%Y-%m-%d")
  year_ago        = (datetime.today() - timedelta(days=365)).strftime("%y%m%d%H%M%S")
  month_ago       = (datetime.today() - timedelta(days=30)) .strftime("%y%m%d%H%M%S")
  day_ago         = (datetime.today() - timedelta(days=1))  .strftime("%y%m%d%H%M%S")
  high_date       = (datetime.today()).strftime("%Y-%m-%d")
  end_date        = (datetime.today()).strftime("%y%m%d%H%M%S")

  for i in range(len(path_http)):
    with open(path_http[i], 'r') as file:
      filedata = file.read()
    filedata = filedata.replace('[comment]', create_comment('http',i,len(path_http)))

    filedata = filedata.replace('[sess_id]', str(sess_id))
    filedata = filedata.replace('[sess_uid]', sess_uid)  
    filedata = filedata.replace('[low_date_year]', str(low_date_year))
    filedata = filedata.replace('[low_date_month]', str(low_date_month))
    filedata = filedata.replace('[low_date_day]', str(low_date_day))
    filedata = filedata.replace('[high_date]', str(high_date))
    filedata = filedata.replace('[year_ago]', year_ago)
    filedata = filedata.replace('[month_ago]', month_ago) 
    filedata = filedata.replace('[day_ago]', day_ago)
  
    filedata = filedata.replace('[end_date]', str(end_date))
    filedata = filedata.replace('[abonent_id]', logins[current_login_num])
    filedata = filedata.replace('[task_create_date]', str(task_create_date))

    cur.execute(filedata)
    con.commit() # save
    current_login_num +=1

  return "[ OK ] http задачи созданы"



def create_task_ips():
  ips = p.get_ips()
  print(len(path_ip))
  print(len(ips))
  if len(path_ip) != len(ips):
    return "[ ERR ] ip задачи не созданы"

  for i in range(len(path_ip)):
    with open(path_ip[i], 'r') as file:
      filedata = file.read()

    filedata = filedata.replace('[comment]', create_comment('ip',i,len(path_ip)))
    clien_ip            = hex(int(ipaddress.IPv4Address(ips[i][0]))).split('x')[-1]
    server_ip           = hex(int(ipaddress.IPv4Address(ips[i][1]))).split('x')[-1]
    destination_nat_ip  = hex(int(ipaddress.IPv4Address(ips[i][2]))).split('x')[-1]

    low_date    = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    high_date   = datetime.today().strftime("%Y-%m-%d")
    start_date  = (datetime.today() - timedelta(days=1)).strftime("%y%m%d%H%M%S")
    end_date    = datetime.today().strftime("%y%m%d%H%M%S")

    filedata = filedata.replace('[sess_id]', str(sess_id))
    filedata = filedata.replace('[sess_uid]', sess_uid)  
    filedata = filedata.replace('[low_date]', str(low_date))
    filedata = filedata.replace('[high_date]', str(high_date))

    filedata = filedata.replace('[start_date]', str(start_date))
    filedata = filedata.replace('[end_date]', str(end_date))

    filedata = filedata.replace('[client_ip]', clien_ip)
    filedata = filedata.replace('[server_ip]', server_ip)
    filedata = filedata.replace('[destination_ip]', destination_nat_ip)

    filedata = filedata.replace('[task_create_date]', str(task_create_date))

    
    cur.execute(filedata)
    con.commit() # save
    time.sleep(2)
  return "[ OK ] ip задачи созданы"

if tasks_abonents == 'True':
  print('Create abonents task...1')
  print(create_task_abonents())
if tasks_http_mask == 'True':
  print('Create http task...8')
  print(create_task_http())
if tasks_ip == 'True':
  print('Create connections task...9')
  print(create_task_ips())

print('Create login day task...' + str(tasks_day))
print(create_task_login(int(tasks_day),1)) # day

print('Create login month task...' + str(tasks_month))
print(create_task_login(int(tasks_month),30)) # month

print('Create login 3 month task...' + str(tasks_3month))
print(create_task_login(int(tasks_3month),90)) # 3month

print('Create login 6 month task...' + str(tasks_6month))
print(create_task_login(int(tasks_6month),180)) # 6month

print('Create login year task...' + str(tasks_year))
print(create_task_login(int(tasks_year),365)) # year


comment_filter = '<!--Comment:/load_tests/' +str(curent_tests).zfill(2)
#comment_filter = '<!--Comment:/load_tests/12'
print(comment_filter)
cur.execute(f"update oimm.tasks set task_tsta_id = 0 where task_body like '{comment_filter}/raw%'")
con.commit() # save
print('[ OK ] raw задачи запущены')

print('Чтобы остановить тесты, введите:')
print(f"su - postgres -c 'psql {db} -p {port} -c \"update oimm.tasks set task_tsta_id = 2 where task_body like '{comment_filter}/%'\"'")

while True:
  cur.execute(f"\
    select * from oimm.tasks\
    where task_body like '{comment_filter}/raw%'\
    and task_tsta_id = 0\
  ")
  result = cur.fetchall()
  print(f"[ LOAD ] В работе еще: {len(result)} задач(raw)")
  if len(result) == 0:
    break
  time.sleep(int(delay_minutes))


cur.execute(f"update oimm.tasks set task_tsta_id = 0 where task_body like '{comment_filter}/ip%'")
con.commit() # save
print('[ OK ] ip задачи запущены')

while True:
  cur.execute(f"\
    select * from oimm.tasks\
    where task_body like '{comment_filter}/ip%'\
    and task_tsta_id = 0\
  ")
  result = cur.fetchall()
  print(f"[ LOAD ] В работе еще: {len(result)} задач(ip)")
  if len(result) == 0:
    break
  time.sleep(int(delay_minutes))

cur.execute(f"update oimm.tasks set task_tsta_id = 0 where task_body like '{comment_filter}/http%'")
con.commit() # save
print('[ OK ] http задачи запущены')

while True:
  cur.execute(f"\
    select * from oimm.tasks\
    where task_body like '{comment_filter}/http%'\
    and task_tsta_id = 0\
  ")
  result = cur.fetchall()
  print(f"[ LOAD ] В работе еще: {len(result)} задач(http)")
  if len(result) == 0:
    break
  time.sleep(int(delay_minutes))



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
  worksheet.write(0, 3+i*2, str(num_tests[i][1]))

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
  worksheet.write( 11, 0, 'Поиск НТТР-соединений по одиночному IP-адресу клиента.')
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
    for j in range(start_c, count_max+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '1 день.')
      worksheet.write( j, 2, '0:01:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))

  start_c +=count_max

  type_tests = 'raw_030'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    for j in range(start_c, count_max+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '30 дней.')
      worksheet.write( j, 2, '0:10:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
  start_c +=count_max

  type_tests = 'raw_090'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    for j in range(start_c, count_max+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '90 дней.')
      worksheet.write( j, 2, '0:15:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
  start_c +=count_max

  type_tests = 'raw_180'
  count_max = p.get_nums_tests_max(type_tests)
  for c in range(count_tests):
    result = p.get_results(c+1,type_tests)
    for j in range(start_c, count_max+start_c):
      worksheet.write( j, 0, 'Поиск недекодированных соединений логину пользователя.')
      worksheet.write( j, 1, '180 дней.')
      worksheet.write( j, 2, '0:15:00')
      worksheet.write( j, 3 + c*2,str(result[j-start_c][0]))
      worksheet.write( j, 4 + c*2,str(result[j-start_c][1]))
  start_c +=count_max


fill_http(len(num_tests))
fill_ip(len(num_tests))
fill_raw(len(num_tests))


workbook.close()

time.sleep(2)


sender_email = FROM
receiver_email = TO

message = MIMEMultipart()

message["From"] = sender_email
message['To'] =  COMMASPACE.join(receiver_email)
message['Subject'] = "Нагрузочные тесты: " + operator_tr 
message.attach(MIMEText('Конфиг сервера:', "plain"))

file = workbook_name
attachment = open(file,'rb')

obj = MIMEBase('application','octet-stream')

obj.set_payload((attachment).read())
encoders.encode_base64(obj)
obj.add_header('Content-Disposition',"attachment; filename= "+file)

message.attach(obj)


my_message = message.as_string()

email_session = smtplib.SMTP_SSL('smtp.yandex.ru',465)
email_session.login(sender_email,PASSWORD)
email_session.sendmail(sender_email,receiver_email,my_message)
email_session.quit()
print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")


con.close() 
