import phylib
import sqlite3
import os

# Constants from phylib
BALL_RADIUS = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS
FRAME_INTERRVAL = 0.01

ballGroupsNotAssigned = True 
checker = 0
player1Balls = None
player2Balls = None

#SVG headers and footer templates for generating SVG files
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
 "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
 
 <rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";
FOOTER = """</svg>\n""";

# Ball colours
BALL_COLOURS = [
    "WHITE", "YELLOW", "BLUE", "RED", "PURPLE", "ORANGE", "GREEN", "BROWN",
    "BLACK", "LIGHTYELLOW", "LIGHTBLUE", "PINK", "MEDIUMPURPLE", "LIGHTSALMON",
    "LIGHTGREEN", "SANDYBROWN"
]

# Coordinate class for wrapping coordinates from phylib 
class Coordinate(phylib.phylib_coord):
    pass

# StillBall class
class StillBall(phylib.phylib_object):
    def __init__(self, number, pos):
        phylib.phylib_object.__init__( self, phylib.PHYLIB_STILL_BALL, number, pos, None, None, 0.0, 0.0)
        self.__class__ = StillBall

    def svg(self):
        # generating SVG for the still ball representation in table
        if (BALL_COLOURS[self.obj.still_ball.number] == 'WHITE'):
            return """<line id="direction-line" x1="%d" y1="%d" x2="0" y2="0" stroke="red" stroke-width="10" visibility="hidden"></line>\n<circle id="cue-ball" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])

        else:
            return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])

# RollingBall class
class RollingBall(phylib.phylib_object):
    def __init__(self, number, pos, vel, acc):
        phylib.phylib_object.__init__( self, phylib.PHYLIB_ROLLING_BALL, number, pos, vel, acc, 0.0, 0.0)
        self.__class__ = RollingBall #matched the python class to the structure in C

    def svg(self):
        # generating svg for the rolling ball on the table
        return """<circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])

# Hole class
class Hole(phylib.phylib_object):
    def __init__(self, pos):
        phylib.phylib_object.__init__( self, phylib.PHYLIB_HOLE, 0, pos, None, None, 0.0, 0.0)
        self.__class__ = Hole #matched hole class to the structure in C

    def svg(self):
        #generating svg for the holes on the table
        return """<circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)

# HCushion class
class HCushion(phylib.phylib_object):
    def __init__(self, y):
        phylib.phylib_object.__init__( self, phylib.PHYLIB_HCUSHION, 0, None, None, None, 0.0, y)
        self.__class__ = HCushion

    def svg(self):
        y_pos = -25 if self.obj.hcushion.y == 0 else 2700
        #generated svg value for horizontal cushion with the assigned values
        return f' <rect width="1400" height="25" x="-25" y="{y_pos}" fill="darkgreen" />\n'

# VCushion class
class VCushion(phylib.phylib_object):
    def __init__(self, x):
        phylib.phylib_object.__init__( self, phylib.PHYLIB_VCUSHION, 0, None, None, None, x, 0.0)
        self.__class__ = VCushion

    def svg(self):
        x_pos = -25 if self.obj.vcushion.x == 0 else 1350
        #generated svg value for vertical cushion with the assigned values
        return f' <rect width="25" height="2750" x="{x_pos}" y="-25" fill="darkgreen" />\n'

# Table class
class Table(phylib.phylib_table):
    def __init__(self):
        phylib.phylib_table.__init__(self)
        self.current = -1 #tracking the object being iterated

    def __iadd__(self, other): #allows += to add objects to table
        self.add_object(other)
        return self

    def __iter__(self): #allows table iteration
        return self

    def __next__(self): #iterated over table object
        self.current += 1
        if self.current < MAX_OBJECTS: #condition to stop at max objects
            return self[self.current]
        self.current = -1
        raise StopIteration #signal to stop iteration

    def __getitem__( self, index ):
        result = self.get_object( index )
        if result==None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment(self):
        result = phylib.phylib_table.segment( self )
        if result:
            result.__class__ = Table
            result.current = -1
        return result

    def svg(self):
        svg_content = HEADER
        for obj in self:
            if obj is not None:
                svg_content += obj.svg()
        svg_content += FOOTER
        return svg_content
    
    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
            # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,Coordinate(0,0),Coordinate(0,0),Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
                # add ball to table
                new += new_ball;
            if isinstance( ball, StillBall ):
            # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,Coordinate( ball.obj.still_ball.pos.x,ball.obj.still_ball.pos.y ) );
                # add ball to table
                new += new_ball;
                # return table
        return new
    
    def cueBall(self, xvel, yvel):
        new_table = Table()
        cue_ball_found = False

        for ball in self:
            if isinstance(ball, StillBall) and ball.obj.still_ball.number == 0:
                # Found the cue ball, now converting it to a RollingBall
                xpos, ypos = ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y
                cue_ball = RollingBall(0, Coordinate(xpos, ypos), Coordinate(xvel, yvel), Coordinate(0, 0))

                # Calculate acceleration due to drag
                speed = phylib.phylib_length(Coordinate(xvel, yvel))
                if speed > VEL_EPSILON:
                    acc_x = (-xvel / speed) * DRAG
                    acc_y = (-yvel / speed) * DRAG
                    cue_ball.obj.rolling_ball.acc.x = acc_x
                    cue_ball.obj.rolling_ball.acc.y = acc_y

                new_table += cue_ball
                cue_ball_found = True
            elif isinstance(ball, StillBall):
                new_table += ball
            elif isinstance(ball,RollingBall):
                 new_table += ball
        if not cue_ball_found:
            raise ValueError("Cue ball not found")

        return new_table


class Database:
    def __init__(self, reset=False):
        self.db_file = "phylib.db"
        if reset and os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def tableExists(self, tableID):
        """Check if a table with the given ID exists in the database."""
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT COUNT(*) FROM TTable WHERE TABLEID = ?", (tableID,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def createDB(self):
        global ballGroupsNotAssigned, player1Balls, player2Balls
        player2Balls = None
        player1Balls = None
        ballGroupsNotAssigned = True
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Ball (
            BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
            BALLNO INTEGER NOT NULL,
            XPOS FLOAT NOT NULL,
            YPOS FLOAT NOT NULL,
            XVEL FLOAT,
            YVEL FLOAT
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS TTable (
            TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
            TIME FLOAT NOT NULL
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS BallTable (
            BALLID INTEGER NOT NULL,
            TABLEID INTEGER NOT NULL,
            FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)
        );''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Game (
            GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
            GAMENAME VARCHAR(64) NOT NULL
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Player (
            PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
            GAMEID INTEGER NOT NULL,
            PLAYERNAME VARCHAR(64) NOT NULL,
            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Shot (
            SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
            PLAYERID INTEGER NOT NULL,
            GAMEID INTEGER NOT NULL,
            FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
            FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
        );''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS TableShot (
            TABLEID INTEGER NOT NULL,
            SHOTID INTEGER NOT NULL,
            FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
            FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
        );''')
        
        # Commit the changes and close the cursor
        self.conn.commit()
        self.cursor.close()

    def readTable(self, tableID):
        self.cursor = self.conn.cursor()
        # SQL starts indexing at 1, so we need to add 1 to our tableID
        sql_tableID = tableID + 1

        # Construct SQL query to join Ball and BallTable tables
        query = """
        SELECT Ball.BALLNO, Ball.XPOS, Ball.YPOS, Ball.XVEL, Ball.YVEL, TTable.TIME
        FROM BallTable
        JOIN Ball ON BallTable.BALLID = Ball.BALLID
        JOIN TTable ON BallTable.TABLEID = TTable.TABLEID
        WHERE BallTable.TABLEID = ?
        """

        # Execute the query
        self.cursor.execute(query, (sql_tableID,))

        # Fetch all the balls for the given table
        balls_data = self.cursor.fetchall()

        # If no balls are found, return None
        if not balls_data:
            return None

        # Create a new table object
        new_table = Table()
        new_table.time = balls_data[0][5]  # Assuming all balls have the same time

        # Add balls to the table
        for ball_data in balls_data:
            ball_no, xpos, ypos, xvel, yvel = ball_data[:5]

            # Check for velocity to determine if the ball is still or rolling
            if xvel is None or yvel is None:  # If velocity is NULL, it's a StillBall
                new_ball = StillBall(ball_no, Coordinate(xpos, ypos))
            else:
                speed = phylib.phylib_length(Coordinate(xvel, yvel))

                # Default acceleration to zero
                acc = Coordinate(0, 0)

                # Check if the speed is significant to apply drag and calculate acceleration
                if speed > VEL_EPSILON:
                    acc.x = (-xvel / speed) * DRAG 
                    acc.y = (-yvel / speed) * DRAG
                    new_ball = RollingBall(ball_no, Coordinate(xpos, ypos), Coordinate(xvel, yvel), acc)

            # Add the new ball to the table
            new_table += new_ball

        # Close the cursor and commit the transaction
        self.cursor.close()
        self.conn.commit()

        return new_table
    
    def writeTable(self, table):
        # Begin a transaction
        self.cursor = self.conn.cursor()

        # Insert a new record into the TTable table and get the inserted TABLEID
        self.cursor.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))
        table_id = self.cursor.lastrowid

        # Insert records into the Ball table
        for ball in table:
            # Check the type of ball and insert appropriate data
            if isinstance(ball, StillBall):
                xvel, yvel = None, None  # Still balls have no velocity
                number = ball.obj.still_ball.number
                xpos, ypos = ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y
            elif isinstance(ball, RollingBall):
                xvel, yvel = ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y
                number = ball.obj.rolling_ball.number
                xpos, ypos = ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y
            else:
                continue  # Skip if it's not a ball

            self.cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                                (number, xpos, ypos, xvel, yvel))
            ball_id = self.cursor.lastrowid

            # Link the ball with the table in the BallTable table
            self.cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ball_id, table_id))

        # Commit the transaction and close the cursor
        self.conn.commit()
        return table_id
    
    def close(self):
        self.conn.commit()
        self.conn.close()

    def getGame(self, gameID):
        self.cursor = self.conn.cursor()
        # Adjust for SQL indexing starting from 1
        sql_gameID = gameID + 1

        # SQL query to fetch game and player details
        query = """
        SELECT Game.GAMEID, Game.GAMENAME, MIN(Player.PLAYERNAME) AS Player1, MAX(Player.PLAYERNAME) AS Player2
        FROM Game
        JOIN Player ON Game.GAMEID = Player.GAMEID
        WHERE Game.GAMEID = ?
        GROUP BY Game.GAMEID
        """

        self.cursor.execute(query, (sql_gameID,))
        result = self.cursor.fetchone()

        if result:
            return result
        else:
            return None

    def setGame(self, gameName, player1Name, player2Name):
        self.cursor = self.conn.cursor()
        # Insert game record
        self.cursor.execute("INSERT INTO Game (GAMENAME) VALUES (?)", (gameName,))
        game_id = self.cursor.lastrowid

        # Insert player 1 record
        self.cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (game_id, player1Name))

        # Insert player 2 record
        self.cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (game_id, player2Name))

        # Commit the transaction
        self.conn.commit()

        return game_id - 1, gameName, player1Name, player2Name
    
    def newShot(self, gameID, playerName):
        # Adjust for SQL indexing starting from 1
        sql_gameID = gameID

        # SQL query to fetch player ID based on playerName and gameID
        query = """
        SELECT PLAYERID FROM Player
        WHERE PLAYERNAME = ? AND GAMEID = ?
        """

        # Execute the query with the provided playerName and gameID
        self.cursor.execute(query, (playerName, sql_gameID))
        result = self.cursor.fetchone()

        # Check if the query returned a result
        if result:
            player_id = result[0]
        else:
            # Handle the case where no matching player is found
            raise ValueError(f"No player found with name '{playerName}' in game ID {gameID}")

        # Insert a new shot record into the Shot table
        self.cursor.execute("INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)", (player_id, sql_gameID))
        shot_id = self.cursor.lastrowid

        # Commit the transaction
        self.conn.commit()

        return shot_id

class Game:
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        # Initialize database connection
        self.db = Database()
        if gameID is not None and gameName is None and player1Name is None and player2Name is None:
            # Fetch game details from the database
            self.getGame(gameID)
        elif gameID is None and all([gameName, player1Name, player2Name]):
            # Store new game details in the database
            self.setGame(gameName, player1Name, player2Name)
        else:
            raise TypeError("Invalid constructor usage")

    def getGame(self, gameID):
        game_details = self.db.getGame(gameID)
        if game_details:
            self.gameID, self.gameName, self.player1Name, self.player2Name = game_details
        else:
            raise ValueError("Game not found")

    def setGame(self, gameName, player1Name, player2Name):
        self.gameID, self.gameName, self.player1Name, self.player2Name = self.db.setGame(gameName, player1Name, player2Name)

    def respawnCueBall(self, table):
        initial_cue_position = Coordinate(675, 2025)  # Create Coordinate with the correct type
        # Create a new StillBall with the initial position
        cue_ball = StillBall(0, initial_cue_position)
        # Remove the current cue ball, if any
        table += cue_ball


    def cueBalltablecheck(self, tempseg):
        # Check each ball in the segment
        new_table = Table();
        for ball in tempseg:

            if(isinstance(ball,HCushion) or isinstance(ball,VCushion) or isinstance(ball,Hole)):
                new_table += ball
            if isinstance(ball,StillBall) and ball.obj.still_ball.number == 0:
                new_table += ball # Found cue ball as a StillBall, so it's not in a hole
            elif isinstance(ball,RollingBall) and ball.obj.rolling_ball.number == 0:
                new_table += ball # Found cue ball as a RollingBall, so it's not in a hole
        # If no cue ball was found in the segment, it must be in a hole
        return new_table
    
    def cueBallinhole(self, tempseg):
        # Check each ball in the segment
        for ball in tempseg:
            if(isinstance(ball,HCushion) or isinstance(ball,VCushion) or isinstance(ball,Hole)):
                continue
            if isinstance(ball,StillBall) and ball.obj.still_ball.number == 0:
                return False # Found cue ball as a StillBall, so it's not in a hole
            elif isinstance(ball,RollingBall) and ball.obj.rolling_ball.number == 0:
                return False # Found cue ball as a RollingBall, so it's not in a hole
        # If no cue ball was found in the segment, it must be in a hole
        return True

    def checkSunkBalls(self):
        # Check the database for the latest set of balls and return the ones that are missing
        self.db.cursor.execute("""
        SELECT Ball.BALLNO 
        FROM Ball
        JOIN BallTable ON Ball.BALLID = BallTable.BALLID
        WHERE BallTable.TABLEID = (SELECT MAX(TABLEID) FROM TTable)
        """)        
        balls_on_table = set(ball_number for (ball_number,) in self.db.cursor.fetchall())
        all_balls = set(range(0, 15))  # Balls 1-15 (excluding the white cue ball)
        sunk_balls = all_balls - balls_on_table
        return sunk_balls
    
    def assignBallGroups(self, playerName, sunk_balls):
        # Determine if the sunk balls are high or low
        low_balls = set(range(1, 8))  # Balls 1-7 are low balls
        high_balls = set(range(9, 16))  # Balls 9-15 are high balls (excluding 8-ball)

        # Find out which group the first sunk ball belongs to
        global player1Balls, player2Balls
        for ball in sorted(sunk_balls):
            if ball == 8:
                continue  # Skip the black ball
            elif ball in low_balls:
                group = 'low'
            elif ball in high_balls:
                group = 'high'
            else:
                continue  # Skip the white ball


            # Assign the group to the current player and the other group to the opponent
            if self.player1Name == playerName:
                player1Balls = group
                player2Balls = 'high' if group == 'low' else 'low'
            else:
                player2Balls = group
                player1Balls = 'high' if group == 'low' else 'low'
            break 
    
    def shoot(self, gameName, playerName, table, xvel, yvel):
        shot_id = self.db.newShot(self.gameID, playerName)
        svg_frames = []
        sendinback = []

        cue_ball = table.cueBall(xvel, yvel)
        if not cue_ball:
            raise ValueError("Cue ball not found")

        temptable = cue_ball
        previously_sunk_balls = self.checkSunkBalls()
        while temptable:
            tempseg = temptable.segment()
            if tempseg is None:
                konsatable = self.cueBalltablecheck(temptable)
                if self.cueBallinhole(konsatable):
                    self.respawnCueBall(temptable)
                table_id = self.db.writeTable(temptable)
                self.db.cursor.execute("INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)", (table_id, shot_id))
                svg_content = temptable.svg()
                svg_frames.append(svg_content)
                break

            for i in range(int((tempseg.time - temptable.time) / FRAME_INTERRVAL)):
                frame_time = i * FRAME_INTERRVAL
                frame_table = temptable.roll(frame_time)
                frame_table.time = temptable.time + frame_time
                svg_content = frame_table.svg()
                svg_frames.append(svg_content)

            temptable = tempseg

        game_over = False
        winner = None

        game_status = self.checkForWin(playerName)

        if game_status == "won":
            game_over = True
            winner = playerName
        elif game_status == "lost":
            game_over = True
            # Determine the loser and set the winner to the other player
            winner = self.player2Name if playerName == self.player1Name else self.player1Name

        sunk_balls = self.checkSunkBalls()
        newly_sunk_balls = sunk_balls - previously_sunk_balls
        global player1Balls, player2Balls, ballGroupsNotAssigned

        extra_turn = False
        if self.playerBallsSunk(playerName, newly_sunk_balls) and 0 not in sunk_balls:
            extra_turn = True
        if ballGroupsNotAssigned and newly_sunk_balls:
            # Assign groups if they haven't been assigned yet
            self.assignBallGroups(playerName, newly_sunk_balls)
            ballGroupsNotAssigned = False
            extra_turn = True  # Player gets an extra turn after assigning groups
            sendinback.extend([svg_frames, player1Balls, player2Balls, extra_turn, game_over, winner])
        else:
            if self.playerBallsSunk(playerName, newly_sunk_balls) and 0 not in sunk_balls:
                extra_turn = True

            sendinback.extend([svg_frames, None, None, extra_turn, game_over, winner])

        self.db.close()
        return sendinback

    def playerBallsSunk(self, playerName, sunk_balls):
        player_balls = player1Balls if playerName == self.player1Name else player2Balls
        group_balls = set(range(1, 8)) if player_balls == 'low' else set(range(9, 16))

        return bool(group_balls & sunk_balls)
    
    def checkForWin(self, playerName):
        all_balls_sunk = {i: False for i in range(1, 16)}
        # Update the status of each ball based on the latest table state
        for ball in self.checkSunkBalls():
            all_balls_sunk[ball] = True

        player_balls = set(range(1, 8)) if (player1Balls if playerName == self.player1Name else player2Balls) == 'low' else set(range(9, 15))

        # Check if all player's balls are sunk
        all_player_balls_sunk = all([all_balls_sunk[ball] for ball in player_balls])

        # Check if the 8 ball is sunk
        black_ball_sunk = all_balls_sunk[8]

        # Player loses if the 8 ball is sunk and any of their balls are still on the table
        if black_ball_sunk and not all_player_balls_sunk:
            return "lost"

        # Player wins if all their balls and the 8 ball are sunk
        if all_player_balls_sunk and black_ball_sunk:
            return "won"

        # No win or loss yet
        return None

