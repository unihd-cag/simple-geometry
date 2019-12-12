from setuptools import setup


with open('geometry/version.py') as fin:
    data = {}
    exec(fin.read(), data)
    version = data['__version__']


if __name__ == '__main__':
    with open('README.md') as fin:
        long_description = fin.read()

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
        install_requires=["dataclasses ; python_version<'3.7'"],
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
    )
