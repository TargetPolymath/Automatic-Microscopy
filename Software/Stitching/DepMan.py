"""
Copyright 2020 Zachary J. Allen

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

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
