from setuptools import setup
import sys

if sys.platform != 'win32':
    print("Error: NCAS is designed for Windows only.")
    sys.exit(1)

setup(
    name='ncas',
    version='1.2.0',
    description='A Netsh Command Automation Script for Wi-Fi management',
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='sub-limal',
    url='https://github.com/sub-limal/ncas',
    py_modules=['ncas'],
    install_requires=[
        'terminaltables',
        'colorama',
        'qrcode'
    ],
    entry_points={
        'console_scripts': [
            'ncas=ncas:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
    ]
)