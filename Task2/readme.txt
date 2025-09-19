Ayham Amreyah-1221058
Omar Shujaieh-1220027
Hassan Karakra-1220501


Multiplayer Quiz Game

Description:
This project is a multiplayer quiz game that uses TCP and UDP protocols.
Players join the game by providing their username and the game starts once the required number of players has joined.
The game asks questions and players answer within a time limit. 
Feedback is provided to each player regarding whether their answer was correct or not.

Requirements for this project:
- Python 3.13 
- The game uses the built-in "socket" and "threading" libraries..

How to Run code in the task 2:

1. Run the Server:
   - Open a terminal (cmd)
   - Navigate to the folder where the `server.py` file is located using the `cd` command.
	write this command--->(cd C:\Users\coolnet\OneDrive\سطح المكتب\Task2)
  
   - Run the following command to start the server:
     
     python server.py
     
   - The server will start and will wait for players to join.

2. Run the Client(s):
   - Open another terminal window for each client (cmd),(**each player will need a separate terminal).

   - Navigate to the folder where the `client.py` file is located using the `cd` command.
	write this command--->(cd C:\Users\coolnet\OneDrive\سطح المكتب\Task2)	
		
   - Run the following command in each terminal window to start the client:
    
     python client.py
      
   - When prompted, enter a **username** for the player. Example:
     Enter username: Hassan
     

3. How the Game Works:
   - Once the required number of players has joined (as set by `MIN_PLAYERS` in the server code), the game will automatically start.
   - The server will send questions to the players via TCP.
   - Players will have 10 seconds to answer each question.
   - Players should submit their answers by choosing one of the options (a, b, c, or d). Example:
    
     Your answer (a/b/c/d): b
     
   - After each question, the server will provide feedback ("Correct" or "Wrong").
   - After all the questions, the server will announce the final results.

4. Example Gameplay:
   - **Start the server**:
     
     python server.py
    
   - **Start the client** (for each player--> player: Hassan , Ayham , Omar...):
     
     python client.py
     
   - **Enter the username** when prompted:
     
     Enter username: Omar
    

5. Scores and Results:
   - After each question, the server will broadcast the updated scores.
   - At the end of the game, the server will announce the winner based on the total score.

Troubleshooting:
- **Error: `[WinError 10054] An existing connection was forcibly closed by the remote host`**:
  - This error may occur if the server stops or crashes unexpectedly. Ensure the server is running and try reconnecting.

- **Error: `Game Not Starting`**:
  - Make sure that the minimum number of players (`MIN_PLAYERS`) has joined the game before it starts.

Notes:
- The game supports up to **4 players**.
- Each round lasts **10 seconds** for answering.
- You can configure the number of questions and the time per question in the `server.py` file.
- Players are assigned scores based on the correctness of their answers.

Author (make this project):
***(Omar , Hassan ,Ayham)***
