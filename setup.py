from distutils.core import setup

pkg = 'Extensions.RmLocale'
setup (name = 'enigma2-plugin-extensions-rmlocale',
       version = '1.05',
       description = 'plugin for remove unused language files',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
      )
