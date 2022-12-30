#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Tim Wolf",
    author_email='tim.wolf@mpi-hd.mpg.de',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Package to retrieve more complex info from inspire than the web-interface allows",
    entry_points={
        'console_scripts': [
            'ii_get_papers=inspire_info.scripts.get_papers:main',
            'ii_create_cache_file=inspire_info.scripts.create_cache_file:main',
            'ii_create_latex_doc=inspire_info.scripts.create_latex_doc:main',
            'ii_merge_bibtex_files=inspire_info.scripts.merge_bibtex_files:main',
            'ii_create_publication_history=inspire_info.scripts.create_publication_history:main',
            'ii_search_publication_by_title=inspire_info.scripts.search_publication_by_title:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='inspire_info',
    name='inspire_info',
    packages=find_packages(include=['inspire_info', 'inspire_info.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/WolfXeHD/inspire_info',
    version='0.1.14',
    zip_safe=False,
)
