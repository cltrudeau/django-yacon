import os
from setuptools import setup, find_packages
from yacon import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

SETUP_ARGS = dict(
    name='django-yacon',
    version=__version__,
    description='Django based Content Managment building framework',
    long_description=long_description,
    url='https://github.com/cltrudeau/django-yacon',
    author='Christopher Trudeau',
    author_email='ctrudeau+pypi@arsensa.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django,CMS',
    test_suite="load_tests.get_suite",
    install_requires=[
        'Django>=1.11',
        'Pillow>=4.3',
        'bleach>=2.1.1',
        'django-awl>=0.14',
        'django-treebeard>=4.1.2',
    ],
    tests_require=[
    ],
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
