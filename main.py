# main.py

import logging
from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from fastapi import FastAPI, Request, Response
import os
from request_handler import start, help_command, request_handler # , query_handler
from offer_handler import show_offers, create_offer
from base import engine, Base, Session

from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Tables are created here
Base.metadata.create_all(engine)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")

# Initialize python telegram bot
ptb = (
    Application.builder()
    .updater(None)
    .token(TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await ptb.bot.setWebhook("https://parental-giulietta-conesoft-b7c0edc7.koyeb.app/") # replace <your-webhook-url>
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

# Initialize FastAPI app (similar to Flask)
app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

@app.get("/test")
async def test():
    return "esto es una prueba"

ptb.add_handler(CommandHandler("start", start))
ptb.add_handler(CommandHandler("help", help_command))
ptb.add_handler(CommandHandler("offer", create_offer)) # Create offer
ptb.add_handler(CommandHandler("offers", show_offers)) # See all offers
ptb.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, request_handler))
# ptb.add_handler(CallbackQueryHandler(callback=query_handler))