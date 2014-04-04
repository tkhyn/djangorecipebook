"""
djangorecipebook
Buildout recipes for django development
(c) 2014 Thomas Khyn
MIT license (see LICENSE.txt)
"""

from setuptools import setup, find_packages
import os


# imports __version__ variable
exec(open('djangorecipebook/version.py').read())
dev_status = __version_info__[3]

if dev_status == 'alpha' and not __version_info__[4]:
    dev_status = 'pre'

DEV_STATUS = {'pre': '2 - Pre-Alpha',
              'alpha': '3 - Alpha',
              'beta': '4 - Beta',
              'rc': '5 - Production/Stable',
              'final': '5 - Production/Stable'}

# setup function parameters
name = 'djangorecipebook'
setup(
    name=name,
    packages=find_packages(),
    version=__version__,
    description='Buildout recipes for django development',
    long_description=open(os.path.join('README.rst')).read(),
    author='Thomas Khyn',
    author_email='thomas@ksytek.com',
    url='http://open.ksytek.com/djangorecipebook/',  # TODO: check url
    keywords=['django', 'buildout', 'recipe'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: %s' % DEV_STATUS[dev_status],
        'Intended Audience :: ',
        'Framework :: Buildout :: Recipe',
        'Framework :: Django',
        'Topic :: Software Development :: Build Tools',
    ],
    entry_points={'zc.buildout': ['default = %s.recipes.manage:Recipe' % name,
                                  'manage = %s.recipes.manage:Recipe' % name,
                                  'wsgi = %s.recipes.wsgi:Recipe' % name,
                                  'test = %s.recipes.test:Recipe' % name, ]
    }
)
