# offer_handler.py
from models import Offer, TransactionState, User
from base import Session

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def create_offer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with Session() as session:
        with session.begin():
            try:
                await update.message.reply_text('Send your offer description:')
                context.user_data['offer_state'] = TransactionState.WAITING_FOR_DESCRIPTION
            except:
                session.rollback()
            finally:
                session.commit()


async def show_offers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with Session() as session:
        with session.begin():
            try:
                offers = Offer.get_offers(session)
                if not offers:
                    message = "No offers available.\n"
                    await update.message.reply_text(message)
                    return
                message = "Available offers:\n"
                await update.message.reply_text(message)
                context.user_data['bid_query'] = True
                for offer in offers:
                    active_offer_detail = 'Offer ID: {}\n'.format('Offer#' + str(offer.id))
                    active_offer_detail += 'Creator: {}\n'.format(offer.creator.username)
                    active_offer_detail += "Description: {}\n".format(offer.description)
                    reply_markup = InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text='Bid', callback_data='bid/{}'.format(offer.id))],
                                         [InlineKeyboardButton(text='Show Bids',
                                                               callback_data='bidder_bid_review/{}'.format(offer.id))]])
                    await update.message.reply_text(active_offer_detail, reply_markup=reply_markup)
            except:
                session.rollback()
            finally:
                session.commit()