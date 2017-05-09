from board import Board
import mysql.connector

cnx = mysql.connector.connect(user='USERNAME',password='PASSWORD',host='localhost',database='DBNAME')

class BoardDB:
    """ Methods to handle persistent game data storage """
    def readBoard(phone):
        """ Load the current board state and win-loss record for the given phone from the db """
        cursor = cnx.cursor()
        query = ("SELECT board,win,loss,draw FROM connectfour WHERE phone=%s")
        cursor.execute(query, (phone,))
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            cursor = cnx.cursor()
            query = ("INSERT INTO connectfour (phone,created,updated) VALUES (%s,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP) ON DUPLICATE KEY UPDATE phone=VALUES(phone)")
            cursor.execute(query, (phone,))
            cursor.close()
            cnx.commit()
            return (None,0,0,0)
        else:
            (state,win,loss,draw) = row
            cursor.close()
            board = Board()
            if not(state is None):
                board.load(state)
            if win is None:
                win = 0
            if loss is None:
                loss = 0
            if draw is None:
                draw = 0
            return (board,win,loss,draw)

    def saveBoard(phone,board,win,loss,draw):
        """ Save the current board state and win-loss record for the given phone to the db """
        cursor = cnx.cursor()
        query = ("UPDATE connectfour SET board=%s,win=%s,loss=%s,draw=%s,updated=CURRENT_TIMESTAMP WHERE phone=%s")
        cursor.execute(query, (board.save(),win,loss,draw,phone))
        cursor.close()
        cnx.commit()

