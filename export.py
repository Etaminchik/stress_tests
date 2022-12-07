import psycopg2
import xlsxwriter
import datetime
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import *
from email.utils import COMMASPACE, formatdate
import time

f = open('tmp.txt', 'r')
task_creation_date = f.read()

print(task_creation_date)

date = datetime.today().strftime("%d.%m.%Y")
con = psycopg2.connect(
  database="vasexperts", 
  user="oim_admin", 
  password="admin", 
  host="127.0.4.11", 
  port="5434"
)
cur = con.cursor()  

cur.execute("select oper_name from oims.operators")
operator_ru = cur.fetchall()[0][0]

cur.execute(f"select task_high_analyzing_date - task_low_analyzing_date,task_body, task_completion_date - task_start_execution_date, case when task_high_analyzing_date - task_low_analyzing_date = '1 day' then '<1 мин' when task_high_analyzing_date - task_low_analyzing_date = '30 day' then '<10 мин' when task_high_analyzing_date - task_low_analyzing_date = '90 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '180 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '365 day' then '<30 мин' else ' ' end as test, task_report_size, task_body from oimm.tasks t where task_creation_date = '{task_creation_date}' order by task_id")
select = cur.fetchall()



tr = {ord(a):ord(b) for a, b in zip(*symbols)}
operator = operator_ru.translate(tr)
workbook_name = str(operator) + '_' + str(date) + '_LT.xlsx'
workbook = xlsxwriter.Workbook(workbook_name)
worksheet = workbook.add_worksheet('TESTS')

worksheet.write(0, 0, 'Содержание проверки')
worksheet.write(0, 1, 'Диапазон поиска')
worksheet.write(0, 2, 'Норматив выполнения')
worksheet.write(0, 3, 'Время выполнения')
worksheet.write(0, 4, 'Размер результата')


cell_format = workbook.add_format()
cell_format.set_border()
for row in range(len(select)):
    worksheet.write(row+1, 1, str(select[row][0])[:-9])
    worksheet.write(row+1, 2, str(select[row][3]))
    worksheet.write(row+1, 3, str(select[row][2]))
    worksheet.write(row+1, 4, str(select[row][4]))
    if '<abonent-id>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск недекодированных соединений логину пользователя.')
    if 'sliv' in select[row][1] or 'jpeg' in select[row][1]:
        worksheet.write(row+1,0,'Поиск соединений по HTTP-URL с применением символов маскирования *.')
    if '<aaa-login>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск ААА-соединений по IP-адресу пользователя.')
    if '<resource>' in select[row][1] and '<ipv4>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск НТТР-соединений по одиночному IP-адресу клиента.')
    if '<email>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск email-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<im>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск im-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<voip>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск voip-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<file-transfer>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск ftp-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<term-access>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск terminal-соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<raw-flows>' in select[row][1] and '<ipv4>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск недекодированных соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')
    if '<address-translations>' in select[row][1]:
        worksheet.write(row+1,0,'Поиск NAT соединений по IP-адресу (IP клиента, IP сервера объединенные логическим «или»).')



cur.execute(f"select task_high_analyzing_date - task_low_analyzing_date,task_body, task_completion_date - task_start_execution_date, case when task_high_analyzing_date - task_low_analyzing_date = '1 day' then '<1 мин' when task_high_analyzing_date - task_low_analyzing_date = '30 day' then '<10 мин' when task_high_analyzing_date - task_low_analyzing_date = '90 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '180 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '365 day' then '<30 мин' else ' ' end as test, task_report_size, task_body from oimm.tasks t where task_creation_date = '{task_creation_date}' and task_tsta_id = 0 order by task_id")
select = cur.fetchall()
if select == []:
    open('tmp.txt', 'w').close()


workbook.close()

time.sleep(2)


sender_email = FROM
receiver_email = TO

message = MIMEMultipart()

message["From"] = sender_email
message['To'] =  COMMASPACE.join(receiver_email)
message['Subject'] = "Нагрузочные тесты: " + operator_ru + ' ' + date
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
print(my_message)
email_session.sendmail(sender_email,receiver_email,my_message)
email_session.quit()
print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")
