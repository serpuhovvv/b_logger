from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='b_logger',
    version='1.0.0',
    author='serpuhovvv',
    author_email='pudikovserg@gmail.com',
    description='Pytest plugin for logging and combining allure and qase functionality as well as generating lightweight reports',
    long_description=readme(),
    long_description_content_type='text/markdown',
    # url='https://место/где/содержится/информация/на/этот/пакет',
    packages=find_packages(),
    install_requires=['pytest',
                      'pytest-xdist',
                      'allure-pytest',
                      'pathlib',
                      'qase-pytest',
                      'pyyaml',
                      'filelock',
                      'Jinja2',
                      'selenium'],
    python_requires='>=3.12',
    # py_modules=['b_logger'],
    entry_points={
        'pytest11': [
            'b_logger = b_logger.plugin',
        ],
    },
)
