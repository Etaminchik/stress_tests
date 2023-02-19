import configparser
config = configparser.ConfigParser()

config.read('config.conf')


tasks_day = config.get('settings','tasks_day')
tasks_month = config.get('settings','tasks_month')
tasks_3month = config.get('settings','tasks_3month')
tasks_6month =config.get('settings','tasks_6month')
tasks_year =config.get('settings','tasks_year')
tasks_http_mask = config.get('settings','tasks_http_mask') 
tasks_ip = config.get('settings','tasks_connections')
tasks_abonents = config.get('settings','tasks_abonents')

host=config.get('database','host')
port=config.get('database','port')
user=config.get('database','user')
passwd=config.get('database','passwd')
db=config.get('database','db')

delay = config.get('settings','delay')

limit_logins_generic_history = config.get('settings','limit_logins_generic_history')

path_abonents = config.get('templates','abonents')

path_raw_login = config.get('templates','raw_login')

path_http =[]

path_http.append(config.get('templates','http1'))
path_http.append(config.get('templates','http2'))
path_http.append(config.get('templates','http3'))
path_http.append(config.get('templates','http4'))
path_http.append(config.get('templates','http5'))
path_http.append(config.get('templates','http6'))
path_http.append(config.get('templates','http7'))
path_http.append(config.get('templates','http8'))

path_ip = []

path_ip.append(config.get('templates','ip1'))
path_ip.append(config.get('templates','ip2'))
path_ip.append(config.get('templates','ip3'))
path_ip.append(config.get('templates','ip4'))
path_ip.append(config.get('templates','ip5'))
path_ip.append(config.get('templates','ip6'))
path_ip.append(config.get('templates','ip7'))
path_ip.append(config.get('templates','ip8'))
path_ip.append(config.get('templates','ip9'))


FROM = config.get('mail','FROM')
TO = config.get('mail','TO')
PASSWORD = config.get('mail','PASSWORD')

#Костыльная транслитерация без библиотек)))
symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
           u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
