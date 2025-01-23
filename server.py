from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
import sys
import Physics
import phylib
import json
import random

from urllib.parse import parse_qs
play = [1,2]
random.shuffle(play)
temp = play[0]
global isPlayer1Turn
if temp == 1:
    isPlayer1Turn = False
else:
    isPlayer1Turn = True

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/index':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r') as file:
                html_content = file.read()

            # Embed the initial turn information into the HTML
            turn_script = f"<script>var isPlayer1Turn = {str(isPlayer1Turn).lower()};</script>"
            # Ensure the script is inserted before the closing </body> tag
            modified_html = html_content.replace('</body>', turn_script + '</body>')
            self.wfile.write(modified_html.encode('utf-8'))
        elif self.path == '/game-setup':
            cleanup_database()
            self.serve_file('game-setup.html', 'text/html')
        elif self.path.endswith('.svg'):
            self.serve_file(self.path[1:], 'image/svg+xml')
        elif self.path.endswith('.css'):
            self.serve_file(self.path[1:], 'text/css')
        elif self.path.endswith('.js'):
            self.serve_file(self.path[1:], 'application/javascript')
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        if self.path == '/shot':
            # Parse the form data posted
            form_data = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})

            # Extract velocity components and position from the form data
            rb_vel_x = float(form_data.getvalue('velX'))
            rb_vel_y = float(form_data.getvalue('velY'))

            # Delete existing SVG files
            for f in os.listdir('.'):
                if f.endswith('.svg'):
                    os.remove(f)

            db = Physics.Database()
            db.cursor.execute("SELECT MAX(TABLEID) FROM TTable")
            result = db.cursor.fetchone()
            if result[0] is not None:
                table_id = result[0]
            else:
                table_id = None

            table = db.readTable(table_id - 1)

            db = Physics.Database()


            db.cursor.execute("SELECT MAX(GAMEID) FROM Game")
            result = db.cursor.fetchone()

            if result and result[0]:
                db = Physics.Database()
                game_id = result[0]

                # Fetch game information using the game ID
                game_info = db.getGame(game_id-1)
                db = Physics.Database()

                if game_info:
                    _, game_name, player1_name, player2_name = game_info
                    # Instantiate the Game object with retrieved information
                    db = Physics.Database()
                    game = Physics.Game(game_id-1)
                    global temp

                    if  temp == 1:
                        playernme = player1_name
                        temp = 2
                    else:
                        playernme = player2_name
                        temp = 1

                    game_over = False
                    winner = None
                    gotit = []
                    gotit= game.shoot(game_name, playernme, table, rb_vel_x, rb_vel_y)
                    svg_files_list = gotit[0]
                    player1Balls = gotit[1]
                    player2Balls = gotit[2]
                    extra_turn = gotit[3]
                    game_over = gotit[4]
                    winner = gotit[5]
                else:
                    # Handle case where no game info was found
                    print("No game found with ID:", game_id)
            else:
                # Handle case where there are no games in the database
                print("No games found in the database.")
            db = Physics.Database()

            db.close()   # Close the database connection

            global isPlayer1Turn
            if extra_turn:
                if temp == 1:
                    temp = 2
                else:
                    temp =1

            # Send a simple response back
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'Success',
                'message': 'Shot simulated with velocity ({}, {}) and saved to the database.'.format(rb_vel_x, rb_vel_y),
                'svgFiles': svg_files_list,
                'player1Name': player1_name,  # Send Player 1's name
                'player2Name': player2_name,  # Send Player 2's name
                'currentPlayer': player1_name if isPlayer1Turn else player2_name, # Send the name of the current player
                'player1Balls': player1Balls,
                'player2Balls': player2Balls,
                'extraTurn': extra_turn,
                'winner': winner, 
                'gameOver': game_over
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/start-game':
            length = int(self.headers['content-length'])
            post_data = self.rfile.read(length)
            form_data = parse_qs(post_data.decode())

            game_name = form_data.get('gameName')[0]
            player1_name = form_data.get('player1')[0]
            player2_name = form_data.get('player2')[0]
            db = Physics.Database()
            db.createDB()

            # Check if the initial table setup is required
            if not db.tableExists(1):
                RequestHandler.initialtablesetup()

            # Close the database connection
            

            # Initialize the game state
            game = Physics.Game(gameName=game_name, player1Name=player1_name, player2Name=player2_name)

            # Redirect to the game page
            db.close()
            self.send_response(303)
            self.send_header('Location', '/index')  # Adjust as needed
            self.end_headers()
        
    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, 'File Not Found: %s' % filepath)

    def initialtablesetup():
        table = Physics.Table()
        still_balls = [
            # Cue ball
            (0, Physics.Coordinate(675, 2025)),
            # Solid balls
            (1, Physics.Coordinate(672, 640)),   # Yellow ball (1)
            (2, Physics.Coordinate(637, 580)),   # Blue ball (2)
            (3, Physics.Coordinate(705, 580)),   # Red ball (3)
            (4, Physics.Coordinate(605, 526)),   # Purple ball (4)
            (5, Physics.Coordinate(673, 526)),   # Orange ball (5)
            (6, Physics.Coordinate(742, 526)),   # Green ball (6)
            (7, Physics.Coordinate(574, 465)),   # Maroon/Brown ball (7)
            # Black ball
            (8, Physics.Coordinate(637, 465)),   # Black ball (8)
            # Stripe balls
            (9, Physics.Coordinate(705, 465)),   # Yellow stripe (9)
            (10, Physics.Coordinate(772, 465)),  # Blue stripe (10)
            (11, Physics.Coordinate(550, 408)),  # Pink stripe (11)
            (12, Physics.Coordinate(614, 408)),  # Purple stripe (12)
            (13, Physics.Coordinate(680, 408)),  # Orange stripe (13)
            (14, Physics.Coordinate(746, 408)),  # Green stripe (14)
            (15, Physics.Coordinate(813, 408))   # Brown stripe (15)
        ]
        for number, position in still_balls:
                table += Physics.StillBall(number, position)

        db = Physics.Database()
        db.writeTable(table)
        db.close()

def cleanup_database():
    print("\n Cleaning up the database...")
    db = Physics.Database()
    try:
        db.cursor.execute("DROP TABLE IF EXISTS Ball")
        db.cursor.execute("DROP TABLE IF EXISTS TTable")
        db.cursor.execute("DROP TABLE IF EXISTS BallTable")
        db.cursor.execute("DROP TABLE IF EXISTS Game")
        db.cursor.execute("DROP TABLE IF EXISTS Player")
        db.cursor.execute("DROP TABLE IF EXISTS Shot")
        db.cursor.execute("DROP TABLE IF EXISTS TableShot")
        db.conn.commit()
    except Exception as e:
        print(f"Database doesn't exist cleanup: {e}")
    finally:
        db.close()
    print("Database cleanup complete.")


def run(server_class=HTTPServer, handler_class=RequestHandler):
    if len(sys.argv) != 2:
        print("Usage: python3 server.py <port>")
        sys.exit(1)

    try:
        # Get the port number from command-line arguments
        port = int(sys.argv[1])
    except ValueError:
        print("Error: Port number must be an integer.")
        sys.exit(1)

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nExiting server...")
        httpd.server_close()

if __name__ == '__main__':
    # Initialize the database connection

    # Start the server
    run()
