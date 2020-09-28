from telegram.ext import Updater, CommandHandler
import logging
from interpreter import *
import os
import numpy as np


def start(update, context):
    message = "Henllo @{}! Type /help for help.".format(update.effective_user.username)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def help(update, context):
    message = """
        Commands: 

        /help: Display commands
        /guide: How to use this bot
        /run: Parses and runs a quantum circuit
        /example: Loads an example circuit
        /gates: Displays avaliable quantum gates 
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def guide(update, context):
    message = """
    How to use this bot:

    Use the command /run with a quantum circuit as shown in /examples
    The circuit consists of qubits, beging each delimited by a separete line, and
    logical gates (avaliable at /gates). You can use those to perform operations on the qubits
    by adding them to the corresponding qubit line. Other characters other than the gates will be 
    treated as "wires" and can be used to ident the circuit (keep in mind the limit of characters is
    20 per line).
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def gates(update, context):
    message = """
    Currently avaliable logical gates:

    X: NOT/Pauli-X
    Y: Pauli-Y
    Z: Pauli-Z
    H: Hadamard
    M: Measure
    CX,o: Controlled NOT (target: CX, control: o; the 'o' character has to be in the sabe index as the 'C' in its corresponding line)
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def example(update, context):
    examples = {
        'Bell State':
            ['_H_o__M',
            '___CX_M'],
    }

    random_key = np.random.choice(list(examples.keys()))
    random_circ = examples[random_key]

    drawn_circ = '\n'.join(random_circ)

    fname = "{}.png".format(update.effective_chat.id)
    count = parse_and_run(random_circ, fname)
    message=[]
    for state in count.keys():
        message.append(f"{round(count[state]/100,2)}|{state}>")
    message = ' + '.join(message)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Circuit name: {random_key}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=drawn_circ)
    context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(fname, 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    os.remove(fname)


# Parses and runs a quantum circuit
def run(update, context):
    circ_str = context.args

    if (len(circ_str)>5):
        # Too many qubits error
        context.bot.send_message(chat_id=update.effective_chat.id, text="Too many qubits, maximum is 5.")
        return
        
    len_circ = len(circ_str[0])
    if (len_circ>20):
        # Circuit too long error
        context.bot.send_message(chat_id=update.effective_chat.id, text="Circuit is too long. Max characters is 20.")
        return

    for line in circ_str:
        if (len(line) != len_circ):
            # Lines of different lenght
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lines must be the same lenght.")
            return

    fname = "{}.png".format(update.effective_chat.id)
    count = parse_and_run(circ_str, fname)
    message=[]
    for state in count.keys():
        message.append(f"{round(count[state]/100,2)}|{state}>")
    message = ' + '.join(message)

    context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(fname, 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    os.remove(fname)


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")


    TOKEN = os.environ['API_TOKEN']
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("run", run))
    dp.add_handler(CommandHandler("gates", gates))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("example", example))


    updater.start_polling()
    logging.info("=== It's alive! ===")
    updater.idle()
    logging.info("=== Oh no, It's dying! ===")


if __name__ == "__main__":
    main()