import os
import subprocess
import datetime
import glob
from config import xml_dir, archive_path


def archive_xml_files():
	date_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
	archive_file = os.path.join(archive_path, f'aud_{date_str}.tar.xz')

	xml_files = glob.glob(os.path.join(xml_dir, '*.xml'))

	if not xml_files:
		print('not xml files found')

	try:
		print('Start archive')
		subprocess.run(['/usr/bin/tar', '-cvf', archive_file, '--use-compress-program=xz -9'] + xml_files, check=True)

		print('Complete')

		for file in xml_files:
			os.remove(file)
		print('xml files deleted')

	except subprocess.CalledProcessError as e:
		print(f'archiving failed: {e}')
	except Exception as e:
		print(f'Error occurred: {e}')

archive_xml_files()


