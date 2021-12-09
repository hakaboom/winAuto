# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='win-Auto',
    version='1.0.1',
    author='hakaboom',
    author_email='1534225986@qq.com',
    license='Apache License 2.0',
    description='',
    url='https://github.com/hakaboom/winAuto',
    packages=['winAuto'],
    install_requires=['pywinAuto>=0.6.8',
                      "baseImage>=1.0.6",
                      "py-image-registration>=1.0.13",
],
)