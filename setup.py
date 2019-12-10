from setuptools import setup
from sys import version_info

version = '0.1.0'


if __name__ == '__main__':
    with open('README.md') as fin:
        long_description = fin.read()

    dependencies = []
    if version_info < (3, 7):
        dependencies.append('dataclasses')

    setup(
        name='simple-geometry',
        version=version,
        author="Niels Buwen",
        author_email="dev@niels-buwen.de",
        description="A simple geometry library",
        long_description=long_description,
        long_description_content_type='text/markdown',
        package_data={'geometry': ['py.typed']},
        packages=['geometry'],
        install_requires=dependencies,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Intended Audience :: Developers",
            "Operating System :: POSIX :: Linux",
            "Topic :: Software Development",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        ],
