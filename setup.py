from Cython.Build import cythonize

from setuptools import setup, find_packages
from setuptools.extension import Extension

main = Extension('cywrap', ['cywrap.pyx', 'con.c'], include_dirs=['.'], extra_link_args=[
    '-O3  -Wall -W -Wstrict-prototypes -Wwrite-strings  -I. '], runtime_library_dirs=['hiredis/'], libraries=['hiredis'])
# sub = Extension('cyredis', ['cyredis.py'], include_dirs=['.'])

setup(
    name='hiredis_cy',
    version="0.1a",
    ext_modules=cythonize([
        main
    ]),
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    author='Avik S',
    url='https://github.com/aviksama'
)
