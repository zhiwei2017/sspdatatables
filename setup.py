from setuptools import setup, find_packages
import os


source_path = 'src'
# Load README as description of package
with open('README.md') as readme_file:
    long_description = readme_file.read()

# Get current version
with open(os.path.join('VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    name='sspdatatables_pkg',
    version=version,
    author='Zhiwei Zhang',
    author_email='zhiwei2017@gmail.com',
    description='Django package serverside processing datatables',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/zhiwei2017/sspdatatables',
    packages=find_packages(source_path),
    package_dir={'': source_path},
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
