#!/usr/bin/env python3

'''
This code snippet demonstrates how to run a tracking loop
while listening to standard input and waiting for an enter/return
to interrupt the loop for an interactive IPython embed shell.
Upon closing the shell (e.g. ctrl-D), the tracking loop continues.

This can be used to inject further code (adjusting a running
long-term track job for example).
A neat idea is to use hooks to add tasks, e.g. during
each tracking function iteration or at the end of the tracking loop.
The example shows mutable lists which can be managed from the
interactive shell, e.g. by adding callables to tasks_each_turn
or tasks_after_tracking.
(Forgot e.g. to add in the simulation script to pickle some important
information? No problem, add it during the tracking.).

These approaches can help to avoid quitting long lasting jobs
taking e.g. a week to finish.

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

# list of callables which are called each iteration of the tracking loop
# (the local scope variables are passed to the callable as a dict)
tasks_each_turn = []

# list of callables which are called after the tracking loop has terminated
# (the local scope variables are passed to the callable as a dict)
tasks_after_tracking = []

def tracker_code(nturns):
    '''Example code for a tracking loop.'''
    print ('Hit enter to interrupt the tracking!')
    thread, comms = listen()
    for turn in tqdm.tqdm(range(nturns)):
        try:
            # do tracking...
            time.sleep(1)

            for task in tasks_each_turn:
                task(locals())

            if comms:
                # listener received enter/return!
                # call interactive shell with local variables in scope:
                embed()
                thread, comms = listen()
                # return to tracking loop
        except Exception as e:
            print ('Exception was raised, please hit enter/return!')
            thread.join()
            raise e

    for task in tasks_after_tracking:
        task(locals())
    print ('Hit enter to quit the tracking job:')
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
# You can also add functions as tasks to the hook lists, e.g.:
# In [1]: def printer(locals_dict):
#    ...:     print (locals_dict['turn'])
#    ...: tasks_each_turn.append(printer)
# This will add a printed turn at each tracking loop iteration.
# When the tracking has finished you will need to hit enter/return to quit.
