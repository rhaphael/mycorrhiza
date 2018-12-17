
import platform
os_name = platform.system()

linux_path = '~/splitstree4/SplitsTree'
mac_path = '/Applications/SplitsTree/SplitsTree.app/Contents/MacOS/JavaApplicationStub'

if os_name == 'Linux':
	p = linux_path
elif os_name == 'Darwin':
	p = mac_path
else:
	p = linux_path

const = {
	'__SPLITSTREE_PATH__': p
}
