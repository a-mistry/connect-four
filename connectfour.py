#!/usr/bin/env /home4/mistryca/bin/python
# -*- coding: UTF-8 -*-

import cgi
import cgitb
import twilio.twiml
from board import Board, Color
from boarddb import BoardDB

# depth (4 is difficult, 2 is easier, 1 is easy)
difficulty = 1

def nonPersistentGame():
    """ Text prompt interactive game without persistent datastore """
    board = Board()
    board.print()
    while board.winner() is Color.NONE and not board.isDraw():
        # read user input and move
        validInput = False
        move = 0
        while not validInput:
            print('Your move (1-7)?')
            move = input()
            if move.isdigit():
                move = int(move)-1
            else:
                move = -1
            if move<0 or move>6:
                print('That was not a valid move. Please enter a number between 1 and 7')
            elif board.isFull(move):
                print('The column you entered is full. Please select a different column')
            else:
                validInput = True
        board.drop(Color.RED, move)
        
        # check winner
        winner = board.winner()
        if winner is Color.NONE:
            # calculate computer move
            board.drop(Color.BLACK, board.blackMove(difficulty))
            
        # output board
        board.print()
        
    if board.isDraw():
        print('Game ended in a draw')
    elif board.winner() is Color.RED:
        print('Congratulations, you win!')
    else:
        print('Sorry, but you have lost.')
    print('Thank you for playing')

def gameLogic(userPhone,msg):
    """ Runs game logic. Reads from persistent datastore, applies next move, then returns up to two messages of output """
    welcomeMsg = 'Welcome to Connect Four. Send PLAY to start a new game then use numbers 1 to 7 to make moves. HELP for instructions'
    helpMsg = """Reply with
PLAY play a new game
BOARD see board
HELP see instructions
SCORE see win-loss record
RESET clear record & start new game
1-7 drop in given column"""
    msg = msg.lower()
    output = ''
    output2 = None
    (board,win,loss,draw) = BoardDB.readBoard(userPhone)
    if board is None:
        output = welcomeMsg
        board = Board()
        output2 = board.emojiPrint() + "Your move [1-7]?"
    elif msg=="new" or msg=="play":
        board = Board()
        output = board.emojiPrint() + "Your move [1-7]?"
    elif msg=="reset":
        board = Board()
        win = 0
        loss = 0
        draw = 0
        output = "We have cleared your win-loss records"
        output2 = board.emojiPrint() + "Your move [1-7]?"
    elif msg=="board":
        output = board.emojiPrint() + "Your move [1-7]?"
    elif msg=="help":
        output = helpMsg
        output2 = board.emojiPrint() + "Your move [1-7]?"
    elif msg=="score":
        output = "Your record is " + str(win) + " wins, " + str(loss) + " losses, " + str(draw) + " ties"
    elif not(msg.isdigit()) or int(msg)<1 or int(msg)>7:
        output = "That was not a valid move. Please send a number between 1 and 7. Send HELP for instructions"
    elif not(board.winner() is Color.NONE) or board.isDraw():
        output = "The game is over. Send PLAY to start a new game"
    elif board.isFull(int(msg)-1):
        output = "The column you entered is full. Please select a different column\nYour move [1-7]?"
    else:
        board.drop(Color.RED, int(msg)-1)
        winner = board.winner()
        if winner is Color.NONE:
            board.drop(Color.BLACK, board.blackMove(difficulty))
            winner = board.winner()
        output = board.emojiPrint()
        if winner is Color.RED:
            win = win + 1
            output2 = "Congratulations, you have won! Your record is " + str(win) + " wins, " + str(loss) + " losses, " + str(draw) + " ties. Send PLAY to play again"
        elif winner is Color.BLACK:
            loss = loss + 1
            output2 = "Sorry, you have lost. Your record is " + str(win) + " wins, " + str(loss) + " losses, " + str(draw) + " ties. Send PLAY to play again"
        elif board.isDraw():
            draw = draw + 1
            output2 = "The game ended in a draw. Your record is " + str(win) + " wins, " + str(loss) + " losses, " + str(draw) + " ties. Send PLAY to play again"
        else:
            output = output + "Your move [1-7]?"
    BoardDB.saveBoard(phone=userPhone,board=board,win=win,loss=loss,draw=draw)
    return (output,output2)

def commandLineMain():
    """ Uses persistent datastore to run game at command line """
    userPhone = "+19999999999"
    while True:
        msg = input()
        (output,output2) = gameLogic(userPhone,msg)
        print(output)
        if not(output2 is None):
            print(output2)

def twilioMain():
    """ Play connect four over SMS """
    cgitb.enable()
    form = cgi.FieldStorage()
    phone = form['From'].value
    msg = form['Body'].value
    (output,output2) = gameLogic(phone,msg)
    print("Content-type: text/xml\n")
    resp = twilio.twiml.Response()
    resp.message(output)
    if not(output2 is None):
        resp.message(output2)
    print(str(resp))

if __name__ == "__main__":
    twilioMain()
#    commandLineMain()
#    nonPersistentGame()
