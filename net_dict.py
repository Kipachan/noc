import subprocess
from permission_list import decline
#from permission_list import permit

# Функция разрешения доменных имен в ip-адреса и формирование вывода в словарь
def getent_dict(path_to_file):
    net_dict = {}
    with open(path_to_file, 'r') as output_file:
        for domain in output_file:
            domain = domain.strip()  # Удаление символов новой строки
            if domain not in decline:
            	getent_output = subprocess.run(["getent", "ahosts", domain], capture_output=True, text=True)
            	lines = getent_output.stdout.split('\n')

            	# Поиск IP-адресов в строках, содержащих STREAM
            	for line in lines:
             		if 'STREAM' in line:
             			ip_address = line.split()[0]
             			net_dict[ip_address] = domain
    return net_dict
