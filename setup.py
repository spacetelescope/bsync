from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='bsync',
    version='0.1.0',
    author='Justin Quick',
    author_email='jquick@stsci.edu',
    url='',
    license='APACHE 2',
    license_files=('LICENSE',),
    description='rsync for Box.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    project_urls={
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    package_data={

    },
    packages=find_packages(),
    install_requires=[
        'boxsdk[jwt]',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'bsync=bsync.cli:bsync',
        ]
    }
)
