from setuptools import find_packages, setup

# pip install wheel twine
# pip install .

# python setup.py bdist_wheel sdist
# twine check dist/*
# twine upload dist/*

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name="selenium2",
    version="0.1",
    description='A comprehensive Selenium wrapper designed to simplify browser automation and testing tasks.',
    package_dir={"": "."},
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/loudpumpkins/selenium2",
    author="Alexei Panov",
    author_email="alexei_panov@hotmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "selenium==4.2.0"
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.8",
)