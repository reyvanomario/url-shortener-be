def get_real_client_ip(request) -> str:
    client_info = request.scope.get("client")
    if client_info:
        return client_info[0]
    
    if request.client:
        return request.client.host
    
    return "0.0.0.0"

def get_user_ip(request) -> str:
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip
    
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    
    return get_real_client_ip(request)