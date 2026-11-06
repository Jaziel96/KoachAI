"""Tests del deduplicador en Redis (US-016, RF-5): SET NX con TTL de 24 h."""

from unittest.mock import AsyncMock

from app.adapters.dedup.redis_dedup import RedisMessageDeduplicator


async def test_primer_mensaje_se_reclama_con_nx_y_ttl_24h() -> None:
    redis = AsyncMock()
    redis.set.return_value = True
    dedup = RedisMessageDeduplicator(redis)

    assert await dedup.claim("wamid.1") is True
    redis.set.assert_awaited_once_with("wa:msg:wamid.1", "1", nx=True, ex=86400)


async def test_mensaje_repetido_no_se_reclama() -> None:
    redis = AsyncMock()
    redis.set.return_value = None
    assert await RedisMessageDeduplicator(redis).claim("wamid.1") is False


async def test_release_borra_la_clave() -> None:
    redis = AsyncMock()
    await RedisMessageDeduplicator(redis).release("wamid.1")
    redis.delete.assert_awaited_once_with("wa:msg:wamid.1")
