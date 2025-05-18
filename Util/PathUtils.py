import os

class PathUtils:
    
    def project_path() -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
