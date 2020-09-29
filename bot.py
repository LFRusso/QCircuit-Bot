from telegram.ext import Updater, CommandHandler
import logging
from interpreter import *
import os
import numpy as np


def parse_result(count):
    message=[]
    for state in count.keys():
        message.append(f"P(|{state}〉)={round(count[state]/100,2)}")
    message = '\n'.join(message)

    return message


def start(update, context):
    message = "Hello, @{}! Type /help for help.".format(update.effective_user.username)
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def help(update, context):
    message = """
    Commands: 

    /help: Display commands
    /guide: How to use this bot
    /run: Parses and runs a quantum circuit
    /example: Loads an example circuit
    /gates: Displays avaliable quantum gates 

    Code available at https://github.com/LFRusso/QCircuit-Bot
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def guide(update, context):
    message = """
    How to use this bot:

    Use the command /run with a quantum circuit as shown in /examples
    The circuit consists of qubits, being each delimited by a separete line, and logic gates (avaliable at /gates). You can use those to perform operations on the qubits by adding them to the corresponding qubit line. Other characters other than the gates will be treated as "wires" and can be used to ident the circuit (keep in mind the limit of characters is 20 per line).
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def gates(update, context):
    message = """
    Avaliable logic gates:


    - Single qubit operations
    X: NOT/Pauli-X
    Y: Pauli-Y
    Z: Pauli-Z
    H: Hadamard
    M: Measure
    |: Barrier
    i: Identity
    S: S (π/2) gate
    T: T (π/4) gate 
    0: Reset a qubit to |0〉 state

    - Two qubits operations
    o: Control, used for the controlled operations (the 'o' character has to be in the sabe index as the 'C' on its corresponding line)
    CX: Controlled Not (CNOT)
    CY: Controlled Y
    CZ: Controlled Z
    x,x: Swap (the 'x' characters must have the sabe index on their corresponding lines)

    - Three qubits operations
    t,o,o: Toffoli (CCNOT). The 'o' characters must both have the same index as the 't' character.

    
    About quantum logic gates: https://en.wikipedia.org/wiki/Quantum_logic_gate
    """    
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Runs an example circuit
def example(update, context):
    examples = {
        'Bell State':
            ['-H-o--M',
             '---CX-M'],
        'Deutsch (f=0)':
            ['0iH|-|H-M',
             '0XH|-|i-M'],
        'Deutsch (f=1)':
            ['0iH|i|H-M',
             '0XH|X|i-M'],
        'Deutsch (f(0)=0, f(1)=1)':
            ['0iH|o-|H-M',
             '0XH|CX|i-M'],
        'Deutsch (f(0)=1, f(1)=0)':
            ['0iH|Xo-X|H-M',
             '0XH|iCXi|i-M'],
        'Deutsch-Jozsa (Balanced Oracle)':
            ['0Hi|o...ii|H.M',
             '0Hi|..o..i|H.M',
             '0Hi|....o.|H.M',
             '0XH|CXCXCX|HX.'],
        'Finding multiples of 2^3/r; 7^r mod 15 = 1':
            ['........o..o...iM',
             'H.....ooCZH..o..M',
             'Ho.o.......CZCZHM',
             'X.....t..........',
             '.CX....o.........',
             '...CXXo..........',
             '.......t.........'],
    }


    random_key = np.random.choice(list(examples.keys()))
    random_circ = examples[random_key]

    drawn_circ = '\n'.join(random_circ)

    fname = "{}.png".format(update.effective_chat.id)
    count = parse_and_run(random_circ, fname)
    message = parse_result(count)
    
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Circuit name: {random_key}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=drawn_circ)
    context.bot.sendPhoto(chat_id=update.effective_chat.id, photo=open(fname, 'rb'))
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    os.remove(fname)

# Parses and runs a quantum circuit
def run(update, context):
    circ_str = context.args

    if (len(circ_str)>7):
        # Too many qubits error
        context.bot.send_message(chat_id=update.effective_chat.id, text="Too many qubits, maximum is 7.")
        return
        
    len_circ = len(circ_str[0])
    if (len_circ>20):
        # Circuit too long error
        context.bot.send_message(chat_id=update.effective_chat.id, text="Circuit is too long. Max characters is 20.")
        return

    for line in circ_str:
        if (len(line) != len_circ):
            # Lines of different length
            context.bot.send_message(chat_id=update.effective_chat.id, text="Lines must be the same length.")
            return

    fname = "{}.png".format(update.effective_chat.id)
    count = parse_and_run(circ_str, fname)
    message = parse_result(count)


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