from setuptools import setup
import os


# Load README as description of package
with open('README.md') as readme_file:
    long_description = readme_file.read()

# Get current version
with open(os.path.join('VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='sspdatatables',
    version=version,
    author='KnightConan',
    author_email='7a6869776569@gmail.com',
    description='Django package serverside processing datatables',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/KnightConan/sspdatatables',
    packages=["sspdatatables"],
    include_package_data=True,
    install_requires = [
        'pytz',
        'django',
        'djangorestframework',
    ],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
