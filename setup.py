from setuptools import setup
import zbx2slack

setup(
    name='zbx2slack',
    description='command-line tool for Zabbix Alert Notification to Slack.',
    version=zbx2slack.__version__,
    install_requires=[
        'argparse'
    ],
    entry_points='''
        [console_scripts]
        zbx2slack=zbx2slack:main
    ''',
    py_modules=[
        'zbx2slack'
    ],
    url='https://github.com/laughk/zbx2slack',
    author='Kei Iwasaki',
    author_email='me@laughk.org',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
