# request_handler
from models import User, Offer, BiddingState, TransactionState, Bid
from base import Session
from bid_handler import bid_handler

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with Session() as session:
        with session.begin():
            try: # Check if user doesnt exist create user
                chat_id = update.message.chat_id
                user = User.get_user_by_chat_id(session, chat_id)
                if not user:
                    user = update.effective_user
                    new_user = User(name=user.name, lastname=user.last_name, username=user.username,
                                    chat_id=user.id)
                    session.add(new_user)
            except:
                session.rollback()
            finally:
                session.commit()
                context.user_data['user'] = user
                await update.message.reply_text('Dear {} you are registered successfully.'.format(user.name))
                await help_command(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = [
        "/offer - Create new offer",
        "/offers - See available offers",
        "/myoffers - See your active offers"]
    message = "Available services:\n\n" + "\n".join(commands)
    await update.message.reply_text(message, parse_mode='markdown')


async def request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with Session() as session:
        with session.begin():
            try:
                user = context.user_data.get('user', False) or User.get_user_by_chat_id(session, update.message.chat_id)
                if context.user_data.get('bidding_state', False) == BiddingState.WAITING_FOR_RATE:
                    rate = update.message.text
                    bid = Bid(offer_id=context.user_data['offer_object'].id,
                              bid_rate=rate,
                              buyer_id=user.id)
                    session.add(bid)
                    await update.message.reply_text('Bid created. Rate: {}'.format(rate))
                elif context.user_data.get('offer_state', False) == TransactionState.WAITING_FOR_DESCRIPTION:
                    description = update.message.text
                    context.user_data['description'] = description
                    context.user_data['offer_state'] = TransactionState.WAITING_FOR_CURRENCY
                    await update.message.reply_text('Send currency:')
                elif context.user_data.get('offer_state',
                                           False) == TransactionState.WAITING_FOR_CURRENCY:
                    currency = update.message.text
                    user = context.user_data.get('user', False) or User.get_user_by_chat_id(session, update.message.chat_id)
                    offer = Offer(creator=user, currency=currency,
                                  description=context.user_data['description'])
                    session.add(offer)
                    await update.message.reply_text(
                        'Offer created successfully.')
                    context.user_data['offer_state'] = TransactionState.STALL
            except Exception as e:
                print(e.with_traceback())
                session.rollback()
            finally:
                session.commit()


async def query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bid_handler(update, context)