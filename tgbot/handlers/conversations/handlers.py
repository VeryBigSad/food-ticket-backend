from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.food_tickets import handlers as food_tickets_handlers
import tgbot.handlers.conversations.states_constants as states

register_handler = ConversationHandler(
    entry_points=[CommandHandler("register", onboarding_handlers.command_register)],
    states={
        states.GET_USERNAME: [MessageHandler(Filters.regex(r'\b\S{6}\b'), onboarding_handlers.register)]
    },
    fallbacks=[CommandHandler("back", onboarding_handlers.command_wait)]
)

share_code_handler = ConversationHandler(
    entry_points=[CommandHandler("share_code", food_tickets_handlers.start_share)],
    states={
        states.GET_USER_TO_SHARE: [MessageHandler(Filters.regex(r'@[\S]+\b'), food_tickets_handlers.command_share_code)]
    },
    fallbacks=[CommandHandler("back", onboarding_handlers.command_wait)]
)

support_handler = ConversationHandler(
    entry_points=[CommandHandler("support", onboarding_handlers.command_support)],
    states={
        states.GET_REPORT: [MessageHandler(Filters.all, onboarding_handlers.get_report)]
    },
    fallbacks=[CommandHandler("back", onboarding_handlers.command_wait)]
)