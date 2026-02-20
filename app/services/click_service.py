from .. import models
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..exceptions.url_exception import UrlNotFoundError
from user_agents import parse
import httpx
from .. import models
from ..core.redis import redis_client
from ..utils.ip_utils import get_user_ip, get_real_client_ip


async def track_click(short_url: str, db: Session, request):
    statement = select(models.Url).where(models.Url.short_url == short_url)

    url = db.scalar(statement)

    if url is None:
        raise UrlNotFoundError()
    
    user_ip = get_user_ip(request)
        
    
    connection_ip = get_real_client_ip(request)
    
    
    ua_string = request.headers.get("user-agent", "")
    ua = parse(ua_string)

    country = await _get_country(request.client.host)

    if ua.is_mobile:
        device_type = "mobile"
    elif ua.is_tablet:
        device_type = "tablet"
    elif ua.is_pc:
        device_type = "desktop"
    elif ua.is_bot:
        device_type = "bot"
    else:
        device_type = "other"

    click = models.Click(
        url_id=url.id,
        short_url=short_url,
        ip_address=user_ip,
        user_agent=ua_string,
        country=country,
        device_type=device_type,
        browser=ua.browser.family,
        os=ua.os.family
    )

    db.add(click)
    db.commit()
    db.refresh(click)

    await redis_client.incr(f"clicks:{short_url}")
    await redis_client.expire(f"clicks:{short_url}", 86400)


async def _get_country(ip: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            print(ip)
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=countryCode")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("countryCode", "")
    except:
        pass
    return ""
