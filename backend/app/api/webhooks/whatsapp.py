"""Webhook de WhatsApp Cloud API (US-016).

`GET` verifica el endpoint con Meta; `POST` valida la firma, parsea, deduplica,
encola y responde 200 de inmediato. No procesa ni invoca IA: solo encola.
"""

from __future__ import annotations

import hmac
import json
from functools import lru_cache
from typing import Annotated

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.adapters.dedup.redis_dedup import RedisMessageDeduplicator
from app.adapters.queue.log_only import LogOnlyMessageQueue
from app.adapters.whatsapp.parser import parse_webhook_payload
from app.adapters.whatsapp.signature import verify_signature
from app.core.config import get_settings
from app.core.logging import get_logger
from app.ports.dedup import MessageDeduplicator
from app.ports.queue import MessageQueue

router = APIRouter()
logger = get_logger(__name__)

MAX_BODY_BYTES = 1_000_000


@lru_cache
def get_deduplicator() -> MessageDeduplicator:
    client = redis.from_url(str(get_settings().REDIS_URL))  # type: ignore[no-untyped-call]
    return RedisMessageDeduplicator(client)


@lru_cache
def get_message_queue() -> MessageQueue:
    return LogOnlyMessageQueue()


@router.get("/webhooks/whatsapp", response_class=PlainTextResponse)
async def verify_webhook(
    mode: Annotated[str | None, Query(alias="hub.mode")] = None,
    token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
    challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
) -> str:
    esperado = get_settings().WHATSAPP_VERIFY_TOKEN.get_secret_value()
    if mode != "subscribe" or token is None or challenge is None:
        raise HTTPException(status_code=403)
    if not hmac.compare_digest(token.encode(), esperado.encode()):
        raise HTTPException(status_code=403)
    return challenge


@router.post("/webhooks/whatsapp")
async def receive_webhook(
    request: Request,
    dedup: Annotated[MessageDeduplicator, Depends(get_deduplicator)],
    queue: Annotated[MessageQueue, Depends(get_message_queue)],
) -> dict[str, str]:
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413)
    body = await request.body()
    if len(body) > MAX_BODY_BYTES:
        raise HTTPException(status_code=413)

    secret = get_settings().WHATSAPP_APP_SECRET.get_secret_value()
    if not verify_signature(body, request.headers.get("X-Hub-Signature-256"), secret):
        logger.warning("whatsapp_webhook_invalid_signature")
        raise HTTPException(status_code=403)

    try:
        payload = json.loads(body)
    except ValueError:
        raise HTTPException(status_code=400) from None

    for message in parse_webhook_payload(payload):
        if not await dedup.claim(message.message_id):
            logger.info("whatsapp_message_duplicate", message_id=message.message_id)
            continue
        try:
            await queue.enqueue_incoming(message)
        except Exception:
            # Sin esto el reintento de Meta se descartaría como duplicado.
            await dedup.release(message.message_id)
            raise
    return {"status": "ok"}
