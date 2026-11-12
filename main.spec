import os


def get_project_files(source_dir, exclude_dirs):
    added_files = []
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith('__pycache__') and d != '.venv']
        
        for file in files:
            if file.endswith('.spec') or file.endswith('.pyc') or '.git' in root:
                continue
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, source_dir)
            
            dest_path = '' if rel_path == '.' else rel_path
            added_files.append((full_path, dest_path))
            
    return added_files

exclude_list = ['ui', '.vscode', '.venv', 'build', 'dist']

project_datas = get_project_files('.', exclude_list)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=project_datas, 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Без черного окна консоли
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    disable_command_line5=None,
)