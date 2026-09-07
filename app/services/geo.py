import httpx

from app.config import settings


def provider_a(ip: str):
    if not settings.geo_provider_a_enabled:
        raise RuntimeError("Provider A disabled")

    response = httpx.get(
        f"http://ip-api.com/json/{ip}",
        timeout=3,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError("Provider A failed")

    return {
        "country": data.get("country"),
        "city": data.get("city"),
        "provider": "ip-api",
    }


def provider_b(ip: str):
    if not settings.geo_provider_b_enabled:
        raise RuntimeError("Provider B disabled")

    response = httpx.get(
        f"https://ipapi.co/{ip}/json/",
        timeout=3,
    )
    response.raise_for_status()

    data = response.json()

    if not data.get("country_name"):
        raise RuntimeError("Provider B failed")

    return {
        "country": data.get("country_name"),
        "city": data.get("city"),
        "provider": "ipapi",
    }


def enrich_ip(ip: str):
    try:
        return provider_a(ip)
    except Exception:
        pass

    try:
        return provider_b(ip)
    except Exception:
        return {
            "country": None,
            "city": None,
            "provider": None,
        }