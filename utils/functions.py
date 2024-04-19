def set_project_directory():
    import sys
    from pathlib import Path
    
    BASE_DIR : str = str(Path(__file__).resolve().parent.parent) + '/'
    sys.path.append(BASE_DIR)

set_project_directory()