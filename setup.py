from setuptools import setup

setup(
    name='addbook',
    packages=['addbook'],
    include_package_data=True,
    install_requires=[
        'flask', 'elasticsearch', 'elasticsearch_dsl'
    ],
)