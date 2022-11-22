import psycopg2
import xlsxwriter
import datetime
#from datetime import datetime, timedelta


con = psycopg2.connect(
  database="vasexperts", 
  user="oim_admin", 
  password="admin", 
  host="127.0.6.8", 
  port="5434"
)
cur = con.cursor()  

cur.execute("select task_high_analyzing_date - task_low_analyzing_date,task_body, task_completion_date - task_start_execution_date, case when task_high_analyzing_date - task_low_analyzing_date = '1 day' then '<1 мин' when task_high_analyzing_date - task_low_analyzing_date = '30 day' then '<10 мин' when task_high_analyzing_date - task_low_analyzing_date = '90 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '180 day' then '<15 мин' when task_high_analyzing_date - task_low_analyzing_date = '365 day' then '<30 мин' else ' ' end as test from oimm.tasks t where task_sess_id = 9 order by task_id")
select = cur.fetchall()
workbook = xlsxwriter.Workbook('table_name' + '.xlsx')
worksheet = workbook.add_worksheet('MENU')

worksheet.write(0, 0, 'Содержание проверки')
worksheet.write(0, 1, 'Диапазон поиска')
worksheet.write(0, 2, 'Норматив выполнения')
worksheet.write(0, 3, 'Время выполнения')

cell_format = workbook.add_format()
cell_format.set_border()

for row in range(len(select)):
    worksheet.write(row+1, 1, str(select[row][0])[:-9])
    worksheet.write(row+1, 2, str(select[row][3]))
    worksheet.write(row+1, 3, str(select[row][2]))
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





workbook.close()
