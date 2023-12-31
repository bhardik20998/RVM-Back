# RVM.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['manage.py'],
             pathex=['/Users/hardik/Documents/GitHub/RVM-Back'],
             binaries=[],
             datas=[('/Users/hardik/Documents/GitHub/RVM-Frontend/dist', 'RVM-Frontend/dist')],
             hiddenimports=[
                 'APIs',  # Add all your app names
                 'django',
                 'RVM',  # Add your project name
                 'pkg_resources.py2_warn',
                 'django.core.management',
                 'django.core.management.commands.runserver',
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='RVM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)