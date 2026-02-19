"""
XenForo Forum Archiver - Paket Kurulum Dosyası
"""

from setuptools import setup, find_packages
from pathlib import Path

# README dosyasını oku
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='xenforo-forum-archiver',
    version='1.0.0',
    author='cvv2com',
    description='XenForo v2.x forumlarından içerik çekip statik web sitesine dönüştüren araç',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cvv2com/xenforo-forum-archiver',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.15.0',
        'beautifulsoup4>=4.12.0',
        'requests>=2.31.0',
        'lxml>=4.9.0',
        'python-dotenv>=1.0.0',
        'tqdm>=4.66.0',
        'Jinja2>=3.1.0',
        'cloudscraper>=1.2.71',
        'Pillow>=10.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'xenforo-archiver=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['templates/*.html'],
    },
)
