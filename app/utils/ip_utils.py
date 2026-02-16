def get_real_client_ip(request) -> str:
    """
    Dapatkan IP asli client dengan mengabaikan bug Starlette
    """
    # Ambil dari scope (ini yang paling original)
    client_info = request.scope.get("client")
    if client_info:
        return client_info[0]
    
    # Fallback ke request.client.host (tapi ini sudah terlanjur diubah)
    if request.client:
        return request.client.host
    
    return "0.0.0.0"

def get_user_ip(request) -> str:
    """
    Dapatkan IP asli user (dari header proxy)
    """
    # Prioritaskan header dari proxy
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip
    
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        # IP asli adalah yang paling kiri
        return x_forwarded_for.split(",")[0].strip()
    
    # Fallback ke IP koneksi
    return get_real_client_ip(request)