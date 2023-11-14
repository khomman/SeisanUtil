from setuptools import find_packages, setup

setup(
    name='SeisanUtil',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'seisanutil=SeisanUtil.scripts.seisanutil:run'
        ] 
    }
)
