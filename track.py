#!/usr/bin/env python3

'''
This code snippet demonstrates how to run a tracking loop
while listening to standard input and waiting for an enter/return
to interrupt the loop for an interactive IPython embed shell.
Upon closing the shell (e.g. ctrl-D), the tracking loop continues.

This can be used to inject further code (adjusting a running
long-term track job for example) or to modify a "finish"
function which is called after the end of the tracking loop,
e.g. to schedule additional post processing tasks after the tracking
(e.g. forgot to add in the code to pickle some important information?).

@author: Adrian Oeftiger
@date: 05.01.2021
'''

import threading

# imports for demo purpose:
import time, tqdm
from IPython import embed

def listen():
    '''Spawn a thread which listens for an enter/return.
    Return the thread and an empty list.
    As soon as the thread receives an enter/return from
    standard input, the empty list mutates to become [True]
    and the thread dies.
    '''
    def listening_thread(comms):
        input()
        comms.append(True)
    comms = []
    thread = threading.Thread(
        target=listening_thread,
        args=(comms,),
        daemon=True)
    thread.start()
    return thread, comms

# example:

def finish():
    '''Called after the tracking loop ends.'''
    pass

def tracker_code(nturns):
    '''Example code for a tracking loop.'''
    thread, comms = listen()
    for turn in tqdm.tqdm(range(nturns)):
        # do tracking...
        time.sleep(1)

        if comms:
            # listener received enter/return!
            # call interactive shell with local variables in scope:
            embed()
            thread, comms = listen()
            # return to tracking loop
    finish()
    thread.join()

# WHY ALL THIS?
###
# run this example code e.g. with 
# >>> tracker_code(10)
# and hit enter during the progress bar in order to
# interrupt the tracking and drop into an interactive IPython shell.
# You can access all variables in scope such as turn,
# the tracking state (the beam object or whatever) etc.
# Exit the interactive IPython shell by ctrl-D to resume tracking.
# You can also override the finish function which is called
# after the tracking, e.g. to add pickling the beam object etc.
