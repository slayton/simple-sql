from setuptools import setup, find_packages

setup(
    name='connect-postgres-py',
    version='1.0',
    url='https://github.com/sevenrooms/connect-postgres-py',
    author='slayton',
    author_email='stuart.layton@sevenrooms.com',
    packages=find_packages(),
    install_requires=[
        'psycopg2',
        'pydantic'
    ]
)