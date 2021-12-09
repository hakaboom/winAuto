# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='win-Auto',
    version='1.0.2',
    author='hakaboom',
    author_email='1534225986@qq.com',
    license='Apache License 2.0',
    description='',
    url='https://github.com/hakaboom/winAuto',
    packages=find_packages(),
    install_requires=['pywinAuto>=0.6.8',
                      "baseImage>=1.0.8",
                      "py-image-registration>=1.0.14",
],
)