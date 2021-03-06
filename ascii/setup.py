from setuptools import setup

setup(
    name='asciiart',
    version='0.3',
    py_modules=['asciiart'],
    install_requires=[
        'Click',
        'Pillow'
    ],
    entry_points='''
        [console_scripts]
        ascii=ascii:process
    '''
)
