"""
Publish a new version:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload dist/*
"""
import codecs
from setuptools import setup


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setup(
    name='email-keyword-matcher',
    packages=['email_keyword_matcher'],
    version='1.0.0',
    description='Use respond to an email to trigger specific callbacks.',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    author='Audrow Nash',
    author_email='audrow@hey.com',
    url='https://github.com/audrow/email-keyword-matcher',
    keywords=[
        'email',
    ],
    install_requires=[
        'pytest',         # a testing framework
        'pytest-cov',     # checks the test coverage
        'pytest-flake8',  # check code style for pep-8
        'pytest-mock',    # for mocks
        'pep257',         # check the code is well documented
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Natural Language :: English',
    ],
    python_requires='>=3.6',
)
