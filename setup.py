import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

test_requirements = [
    'pytest<5',  # py2 compatibility
]

release_requirements = [
    'twine>=1.13.0,<2',  # py2 compatibility
]


setup(
    name='mkdocs-redirects',
    version='1.0.3',
    description='A MkDocs plugin for dynamic page redirects to prevent broken links.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    keywords='mkdocs redirect',
    url='https://github.com/datarobot/mkdocs-redirects',
    author='Dustin Burke',
    author_email='dustin@datarobot.com',
    license='MIT',
    python_requires='>=2.7',
    install_requires=[
        'mkdocs>=1.0.4,<2',
        'six>=1.15.0,<2',
    ],
    extras_require={
        'dev': test_requirements + release_requirements,
        'test': test_requirements,
        'release': release_requirements,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'redirects = mkdocs_redirects.plugin:RedirectPlugin'
        ]
    }
)
