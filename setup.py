from setuptools import find_packages, setup
import os
import io
import re

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())

setup(
    name='dsc_wait_prediction',
    packages=find_packages(),
    version="0.0.1",
    url="https://github.com/booleangabs/dsc_wait_prediction",
    author="José Gabriel Pereira Tavares",
    author_email="gabrieltavares1303@gmail.com",
    long_description=read("README.md"),
    description='Submission to Data Science Challenge @ EEF promoted by ITA - Brazil',
    license='MIT',
)
