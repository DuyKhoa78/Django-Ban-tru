from core.models import CauHinhHeThong

def sys_config(request):
    try:
        ht = CauHinhHeThong.get()
        return {'SYS_CONFIG': ht}
    except Exception:
        return {}
