from variables import *
from datetime import datetime, timedelta

class Selects():
    def __init__(self,cur_,count_tasks_,task_create_date_,limit_logins_generic_history_):
        self.cur = cur_
        self.count_tasks = count_tasks_
        self.task_create_date = task_create_date_
        self.limit_logins_generic_history=limit_logins_generic_history_
      


    def get_operator(self):
        self.cur.execute("select oper_name from oims.operators")
        return self.cur.fetchall()[0][0]

    def get_nums_tests(self):
        self.cur.execute("\
            select substring(task_body,25,2)::int as num,\
            task_creation_date \
            from oimm.tasks\
            where task_body like '<!--Comment:/load_tests/%'\
            group by num,task_creation_date \
            order by num")
        return self.cur.fetchall()

    def get_nums_tests_max(self,type_tasks):
        self.cur.execute(f"\
            select max(a.c) from\
            (select substring(task_body,25,2)::int as num,\
            count(*) as c\
            from oimm.tasks\
            where task_body like '<!--Comment:/load_tests/%{type_tasks}%'\
            group by num,task_creation_date \
            order by num) as a")
        return self.cur.fetchall()[0][0]

    def get_results(self,num,type_tests):
        self.cur.execute(f"\
            select task_completion_date - task_start_execution_date as period, \
            task_report_size  from oimm.tasks t \
            where task_body like '<!--Comment:/load_tests/{str(num).zfill(2)}/{type_tests}%'\
            order by task_id ")
        return self.cur.fetchall()



    def get_logins(self):
        date = (self.task_create_date - timedelta(hours = 3)).strftime("%Y-%m-%d")
        self.cur.execute(f"                             \
            SELECT distinct rawf_subscriber_id          \
            FROM oimc.raw_flows                         \
            where rawf_begin_connection_time > '{date}' \
            and rawf_subscriber_id != 'operator'        \
            limit {self.count_tasks}")
        result = self.cur.fetchall()
        logins = []
        for login in result:
            logins.append(login[0])

        if len(logins) < self.count_tasks:
            print('[ WARN ] - Кол-во логинов(', len(logins), ') < тасков(',self.count_tasks, ') -> логины будут повторяться')
            j = 0
            logins2 = []
            for i in range(self.count_tasks):
                if j > len(logins) - 1:
                    j = 0
                logins2.append(logins[j])
                j +=1
            logins = logins2
        return logins


    def find_old_tests(self):
        self.cur.execute(f"                                     \
            select substring(task_body,25,2)::int as number,    \
            substring(task_body,14,30)                          \
            from oimm.tasks                                     \
            where task_body like '<!--Comment:/load_tests/%'    \
            order by number desc")
        result = self.cur.fetchall()
        return result


    def get_logins_generic_history(self):
        self.cur.execute(f"\
            select sgnh_identity\
            from oims.subs_generic_history\
            where sgnh_identity != ''\
            limit {self.limit_logins_generic_history}")
        return self.cur.fetchall()


    def get_ips(self):
        date = (self.task_create_date - timedelta(hours = 3)).strftime("%Y-%m-%d")
        date_old = (self.task_create_date - timedelta(hours = 35)).strftime("%Y-%m-%d")
        select = f"\
            (select asev_allocated_ip,asev_allocated_ip,asev_allocated_ip, 1 as num\
            from oimc.aaa_session_events\
            where asev_event_time > '{date}'\
            group by asev_allocated_ip\
            order by count(*) desc\
            limit 1)\
            union\
            (select htrq_client_address,htrq_server_address,htrq_server_address, 2 as num\
            from oimc.http_requests\
            where htrq_begin_connection_time > '{date}'\
            group by htrq_client_address,htrq_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select emlc_client_address, emlc_server_address,emlc_server_address,3 as num\
            from oimc.mail_connections\
            where emlc_begin_connection_time > '{date_old}'\
            group by emlc_client_address, emlc_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select imcn_client_address, imcn_server_address,imcn_server_address,4 as num\
            from oimc.im_connections\
            where imcn_begin_connection_time > '{date_old}'\
            group by imcn_client_address, imcn_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select vipc_client_address, vipc_server_address,vipc_server_address,5 as num\
            from oimc.voip_connections\
            where vipc_begin_connection_time > '{date}'\
            group by vipc_client_address, vipc_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select ftpc_client_address, ftpc_server_address,ftpc_server_address,6 as num\
            from oimc.ftp_connections\
            where ftpc_begin_connection_time > '{date}'\
            group by ftpc_client_address, ftpc_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select trmc_client_address, trmc_server_address,trmc_server_address,7 as num\
            from oimc.terminal_connections\
            where trmc_begin_connection_time > '{date}'\
            group by  trmc_client_address, trmc_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select rawf_client_address, rawf_server_address,rawf_server_address,8 as num\
            from oimc.raw_flows\
            where rawf_begin_connection_time > '{date}'\
            group by rawf_client_address, rawf_server_address\
            order by count(*) desc\
            limit 1)\
            union\
            (select adtr_private_address, adtr_public_address, adtr_destination_address,9 as num\
            from oimc.address_translations\
            where adtr_translation_time > '{date}'\
            group by adtr_private_address, adtr_public_address, adtr_destination_address\
            order by count(*) desc\
            limit 1)\
            order by num"
        self.cur.execute(select)
        return self.cur.fetchall()


    def get_sessid(self):
        self.cur.execute("select sess_id, sess_uid  from oimm.sessions where sess_benchboard_uid = 'emulator' and sess_channel_number =1 order by sess_id desc limit 1")
        return self.cur.fetchall()[0]
