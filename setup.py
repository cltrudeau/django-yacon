from setuptools import setup, find_packages

setup(
    name='django-yacon',
    version='0.5.1',
    description='Django based Content Managment building framework',
    long_description=('Yacon is a django app for building websites based on '
        'a CMS.  Yacon provides methods for managing hierarchical, '
        'multi-lingual page content across multple sites.  Yacon ships with '
        'ckedit and uses AJAX calls to allow the user to do inline WYSIWYG '
        'editing of their web content.  Yacon does not provide any design '
        'or templating tools, and so is not a full CMS, but provides '
        'enough to support CMS features on any django site you are already '
        'building.'),
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django,CMS',
    packages=find_packages(),
    install_requires=[
        'Django>=1.7',
        'Pillow>=2.7',
        'bleach>=1.4',
        'django-treebeard>=3',
    ],
)
