from core.config import DEBUG

def log(*args):
    if DEBUG:
        print(*args)
        
