from setuptools import setup, find_packages

setup(
    name='simplesql',
    version='1.0',
    url='https://github.com/slayton/simple-sql',
    author='slayton',
    author_email='stuart.layton@gmail.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        'psycopg2',
        'pydantic'
    ]
)
