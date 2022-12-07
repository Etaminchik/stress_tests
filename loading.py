import psycopg2
from datetime import datetime, timedelta
import ipaddress
import time

# -------------------------------
tasks_day = 30 # Количество тасков
tasks_month = 30 # Количество тасков
tasks_3month = 20 # Количество тасков
tasks_6month = 3 # Количество тасков
tasks_year = 0 # Количество тасков


ip_aaa = '' # Если оставить пустым, возьмется случайное из базы

tasks_http_mask = True # True / False Запускать ли таски на маску http
tasks_connections = True # True / False Запускать ли таски на коннекции по ip
# -------------------------------

count_tasks = tasks_day + tasks_month + tasks_3month + tasks_6month + tasks_year
if tasks_http_mask: count_tasks + 10
if tasks_connections: count_tasks + 10

con = psycopg2.connect(
  database="vasexperts", 
  user="oim_admin", 
  password="admin", 
  host="127.0.0.1", 
  port="54321"
)



task_create_date = (datetime.today() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
print(task_create_date )
cur = con.cursor()  

cur.execute("select oper_name from oims.operators")
operator = cur.fetchall()[0][0]

date_for_login = (datetime.today() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
cur.execute(f"SELECT distinct rawf_subscriber_id  FROM oimc.raw_flows where rawf_begin_connection_time > '{date_for_login}' and rawf_subscriber_id != 'operator' limit 100")
login = cur.fetchall()


if ip_aaa == '':
  date_for_aaa = (datetime.today() - timedelta(hours=3)).strftime("%Y-%m-%d")
  cur.execute(f"select rawf_client_address from oimc.raw_flows where rawf_begin_connection_time > '{date_for_login}' and rawf_subscriber_id != 'operator' limit 1")
  ip_aaa = cur.fetchall()[0][0]


def free_task():
  time.sleep(0.5)
  cur.execute("select task_id from oimm.tasks order by task_id desc limit 1")
  select = cur.fetchall()
  if not select:
    task = 1
  else:
    task = select[0][0] + 1 
  return task


cur.execute("select sess_id, sess_uid  from oimm.sessions where sess_benchboard_uid = 'emulator' and sess_channel_number =1 order by sess_id desc limit 1")
sess_id,sess_uid = cur.fetchall()[0]


def create_task_login(c,days):
  for i in range(c):
    with open('raw-flows_abonent-id.txt', 'r') as file:
      filedata = file.read()
    filedata = filedata.replace('[sess_uid]', sess_uid)

    abonent_id = login[i][0]

    start_date = (datetime.today() - timedelta(days=days) - timedelta(hours=3)).strftime("%y%m%d%H%M%S")
    end_date = (datetime.today() - timedelta(hours=3)).strftime("%y%m%d%H%M%S")
    low_date = (datetime.today() - timedelta(days=days) - timedelta(hours=3)).strftime("%Y-%m-%d")
    high_date = (datetime.today() - timedelta(hours=3)).strftime("%Y-%m-%d")

    filedata = filedata.replace('[start_date]', str(start_date))
    filedata = filedata.replace('[end_date]', str(end_date))
    filedata = filedata.replace('[abonent_id]', abonent_id)
    filedata = filedata.replace('[task_id]', str(free_task()))
    filedata = filedata.replace('[sess_id]', str(sess_id))
    filedata = filedata.replace('[low_date]', str(low_date))
    filedata = filedata.replace('[high_date]', str(high_date))
    filedata = filedata.replace('[task_create_date]', str(task_create_date))

    cur.execute(filedata)
    con.commit() # save


def create_task_http():
  with open('http.txt', 'r') as file:
    filedata = file.read()

  low_date_year = (datetime.today() - timedelta(days=365) - timedelta(hours=3)).strftime("%Y-%m-%d")
  low_date_month = (datetime.today() - timedelta(days=30) - timedelta(hours=3)).strftime("%Y-%m-%d")
  low_date_day = (datetime.today() - timedelta(days=1) - timedelta(hours=3)).strftime("%Y-%m-%d")
  high_date = (datetime.today() - timedelta(hours=3)).strftime("%Y-%m-%d")
  year_ago = (datetime.today() - timedelta(days=365) - timedelta(hours=3)).strftime("%y%m%d%H%M%S")
  month_ago = (datetime.today() - timedelta(days=30) - timedelta(hours=3)).strftime("%y%m%d%H%M%S")
  day_ago = (datetime.today() - timedelta(days=1) - timedelta(hours=3)).strftime("%y%m%d%H%M%S")

  end_date = (datetime.today() - timedelta(hours=3)).strftime("%y%m%d%H%M%S")

  task_id = free_task()

  filedata = filedata.replace('[task_id_1]', str(task_id))
  filedata = filedata.replace('[task_id_2]', str(task_id+1))
  filedata = filedata.replace('[task_id_3]', str(task_id+2))
  filedata = filedata.replace('[task_id_4]', str(task_id+3))
  filedata = filedata.replace('[task_id_5]', str(task_id+4))
  filedata = filedata.replace('[task_id_6]', str(task_id+5))
  filedata = filedata.replace('[task_id_7]', str(task_id+6))
  filedata = filedata.replace('[task_id_8]', str(task_id+7))

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
  filedata = filedata.replace('[abonent_id]', login[0][0])
  filedata = filedata.replace('[task_create_date]', str(task_create_date))
  
  cur.execute(filedata)
  con.commit() # save

def create_task_connections():
  global ip_aaa
  with open('connections.txt', 'r') as file:
    filedata = file.read()

  ip_aaa = hex(int(ipaddress.IPv4Address(ip_aaa))).split('x')[-1]

  low_date = (datetime.today() - timedelta(days=1) - timedelta(hours=3)).strftime("%Y-%m-%d")
  high_date = (datetime.today() - timedelta(hours=3)).strftime("%Y-%m-%d")
  start_date = (datetime.today() - timedelta(days=1) - timedelta(hours=3)).strftime("%y%m%d%H%M%S")
  end_date = (datetime.today() - timedelta(hours=3)).strftime("%y%m%d%H%M%S")

  task_id = free_task()

  filedata = filedata.replace('[task_id_1]', str(task_id))
  filedata = filedata.replace('[task_id_2]', str(task_id+1))
  filedata = filedata.replace('[task_id_3]', str(task_id+2))
  filedata = filedata.replace('[task_id_4]', str(task_id+3))
  filedata = filedata.replace('[task_id_5]', str(task_id+4))
  filedata = filedata.replace('[task_id_6]', str(task_id+5))
  filedata = filedata.replace('[task_id_7]', str(task_id+6))
  filedata = filedata.replace('[task_id_8]', str(task_id+7))
  filedata = filedata.replace('[task_id_9]', str(task_id+8))

  filedata = filedata.replace('[sess_id]', str(sess_id))
  filedata = filedata.replace('[sess_uid]', sess_uid)  
  filedata = filedata.replace('[low_date]', str(low_date))
  filedata = filedata.replace('[high_date]', str(high_date))
  
  filedata = filedata.replace('[start_date]', str(start_date))
  filedata = filedata.replace('[end_date]', str(end_date))
  filedata = filedata.replace('[client_ip]', ip_aaa)
  filedata = filedata.replace('[server_ip]', 'd83ad1ce')
  filedata = filedata.replace('[task_create_date]', str(task_create_date))
  
  #print(filedata)
  cur.execute(filedata)
  con.commit() # save


if tasks_http_mask:
  print('Create http task...8')
  create_task_http()
if tasks_connections:
  print('Create connections task...9')
  create_task_connections()


create_task_login(tasks_day,1) # day
print('Create login day task...' + str(tasks_day))
create_task_login(tasks_month,30) # month
print('Create login month task...' + str(tasks_month))
create_task_login(tasks_3month,90) # 3month
print('Create login 3 month task...' + str(tasks_3month))
create_task_login(tasks_6month,180) # 6month
print('Create login 6 month task...' + str(tasks_6month))
create_task_login(tasks_year,365) # year
print('Create login year task...' + str(tasks_year))

print("select * from oimm.tasks t where task_creation_date = '" + str(task_create_date) + "'")
print('START:')
print("update oimm.tasks set task_tsta_id = 0 where task_creation_date = '" + str(task_create_date) + "'")

with open("tmp.txt", "w") as myfile:
    myfile.write(task_create_date)


con.close() 

