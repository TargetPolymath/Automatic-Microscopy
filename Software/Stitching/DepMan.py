# Dependencies Management

def install_and_import(package, pip_name = None):
	# print("DepMan importing ", package)
	if pip_name is None:
		# print("Smart pip name")
		pip_name = package
	import importlib
	try:
		# print("Trying import...")
		importlib.import_module(package)
	except ImportError:
		import pip
		pip.main(['install','-q', pip_name])
		# print("Installing " + pip_name)
	# finally:
		# print("Done?")
		# globals()[package] = importlib.import_module(package)