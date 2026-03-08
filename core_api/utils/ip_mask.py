"""
Проверка совместимости IP-адреса и маски подсети.
"""
import ipaddress

from django.core.exceptions import ValidationError


def validate_ip_and_mask(ip: str | None, mask: str | None) -> None:
    """
    Проверяет, что маска является корректной маской подсети и что IP и маска
    совместимы (одна версия протокола). При несоответствии поднимает ValidationError.
    """
    if not ip or not mask:
        return
    try:
        ip_obj = ipaddress.ip_address(ip)
        mask_obj = ipaddress.ip_address(mask)
    except ValueError:
        return  # невалидный IP/маска отловит форма
    if ip_obj.version != mask_obj.version:
        raise ValidationError(
            "IP-адрес и маска должны быть одной версии (IPv4 или IPv6)."
        )
    try:
        if ip_obj.version == 4:
            ipaddress.IPv4Network((ip, mask), strict=False)
        else:
            ipaddress.IPv6Network((ip, mask), strict=False)
    except ValueError as e:
        raise ValidationError(
            "Некорректная маска подсети или IP не относится к данной маске."
        ) from e
