from setuptools import setup, find_packages

setup(
    name='simplesql',
    version='1.0',
    url='https://github.com/slayton/simple-sql',
    author='slayton',
    author_email='stuart@stuartlayton.com',
    packages=find_packages(),
    install_requires=[
        'psycopg2'
        'pydantic'
    ]
)