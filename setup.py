from setuptools import find_packages, setup

with open('requirements.txt', 'rt') as requirements:
    requires = requirements.readlines()

setup(name='application',
      version='0.9.1',
      description='Dashboard for F5',
      long_description=open('README.md').read(),
      author='Thomas Kim',
      author_email='iam@thomaskim.net',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      install_requires=requires,
      keywords='python3',
      url='https://github.com/mrthomaskim/f5dashboard',
      download_url='https://github.com/mrthomaskim/f5dashboard',
      platforms=['OS Independent'],
      classifiers=[
          'Development Status :: 1 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.6',
          'Operating System :: OS Independent',
      ],
      entry_points={
          'console_scripts': 'f5dashboard = f5dashboard.__main__:main',
      }
)

