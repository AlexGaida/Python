from setuptools import setup, find_packages
from glob import glob
__version__ = "1.0.0"

# add readme
with open('README.md', 'r') as f:
    LONG_DESCRIPTION = f.read()

# add dependencies
with open('requirements.txt', 'r') as f:
    INSTALL_REQUIRES = f.read().strip().split('\n')

setup(
    name='pipeline.maya.Python',
    version=__version__,
    author='Alexei Gaidachev',
    author_email='gaidachevalex@gmail.com',
    description='Sphinx setup for Maya pipeline project.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    package_dir={'Pipeline': 'pipeline.Maya.Python'},
    platforms = ["Linux", "Mac", "Windows"],
    include_package_data=True,
    setup_requires=[
        'numpy'
    ],
    python_requires='>=3.1.0',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.1.0',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=INSTALL_REQUIRES,
    zip_safe=True,
    license='License :: BSD3 License',
)