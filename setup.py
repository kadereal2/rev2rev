from setuptools import setup
from setuptools import find_packages

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name="revpkg",
    version="0.0.10",
    author="Daniel,Amanda,Ridiwan $ Irene",
    description="AI model for text classification",
    packages=find_packages(),
    install_requires=requirements
)

