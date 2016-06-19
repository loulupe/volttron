from setuptools import setup, find_packages

packages = find_packages('.')
package = packages[0]

setup(
      name = package + 'agent',
      version = "0.1",
      install_requires = ['voltron'],
      packages = packages,
      entry_points = {
           'setuptools.installation':[
               'eggsecutable = ' + package + '.testagent:main',
	    ]
      }
)
