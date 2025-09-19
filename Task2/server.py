import socket
import threading
import random
import time


####----------------------------------------------------------------------------
# dateils the user - id -----> 1220027 , Omar Shujaieh , (TCP=3027 , UDP=6122)
                    #id -----> 1220501 , Hassan Karakra , (TCP=3501 , UDP=6122)
                    #id -----> 1221058 , Ayham Amreyah , (TCP=3058 , UDP=6122)

STUDENT_ID = "1220501"  # Hassan Karakra
TCP_PORT = int(STUDENT_ID[-3:]) + 3000  # 3501
UDP_PORT = int(STUDENT_ID[:3]) + 6000  # 6122
### dateils game 
MIN_PLAYERS = 2  ### Min of players in the game 
MAX_PLAYERS = 4
TIME_PER_Q = 10
NUM_QUESTIONS = 5
####----------------------------------------------------------------------------


players = {}  # username -> {'conn': conn, 'addr': (ip,port), 'score': 0, 'udp_addr': (ip,port)}
lock = threading.Lock()
game_started = False

######## -----------------Game questions -----------------
### answer questions (1-b , 2-b , 3-a , 4-c , 5-b)  
QUESTIONS = [
    ("1-Which of the following can be used by the receiver to order the packets???",
     ["Timer", "Sequence number",
      "Checksum", "None of the above"], "b"),

    ("2-Which protocol is connectionless?",
     ["TCP", "UDP", "Both", "None"], "b"),

    ("3-In TCP, the timeout interval is a function of ",
     ["Estimated RTT at the transmitter ", "Maximum segment size and the overhead of a datagram ",
      "The size of the buffer at the receiver", "None of the above"], "a"),

    ("4-E-mail is:",
     ["Loss-tolerant application ", "Bandwidth-sensitive application ",
      "Elastic application", "None of the above"], "c"),

    ("5-What does DNS resolve?",
     ["IP -> MAC", "URL -> IP", "Port -> Process", "None"], "b"),
]

def format_question(idx, q, opts):
    letters = ['a', 'b', 'c', 'd']
    lines = [f"Q{idx}: {q}"]
    for i, opt in enumerate(opts):
        lines.append(f"{letters[i]}) {opt}")
    lines.append(f"You have {TIME_PER_Q} seconds.")
    lines.append("SEND ANSWER VIA UDP AS: username|a/b/c/d")
    return "\n".join(lines)

### This function broadcasts message to all connected players via their tcp connection
def broadcast_tcp(msg):
    dead = []
    for u, info in players.items():
        try:
            info['conn'].sendall((msg if msg.endswith("\n") else msg + "\n").encode())
        except:
            dead.append(u)
    for u in dead:
        try:
            players[u]['conn'].close()
        except:
            pass
        del players[u]

# ----------This function handle a new player connection--------------
def handle_client(conn, addr):
    global game_started
    try:
        conn.sendall(b"Welcome. Send: JOIN <username>\n")
        data = conn.recv(1024)
        if not data:
            conn.close(); return
        line = data.decode().strip()
        if not line.startswith("JOIN "):
            conn.sendall(b"ERROR Invalid command\n")
            conn.close(); return
        username = line[5:].strip()
        with lock:
            if game_started:
                conn.sendall(b"ERROR GameAlreadyStarted\n")
                conn.close(); return
            if username in players:
                conn.sendall(b"ERROR UsernameTaken\n")
                conn.close(); return
            if len(players) >= MAX_PLAYERS:
                conn.sendall(b"ERROR LobbyFull\n")
                conn.close(); return
            players[username] = {'conn': conn, 'addr': addr, 'score': 0, 'udp_addr': None}
        conn.sendall(f"OK JOINED {username}\n".encode())
        broadcast_tcp(f"LOBBY COUNT {len(players)}/{MIN_PLAYERS}")
    except:
        try: conn.close()
        except: pass



# this function waits for the required number of players to join the game
def wait_and_start():

    global game_started

    while True:
        with lock:
            if len(players) >= MIN_PLAYERS:
                break
        time.sleep(0.2)
    with lock:
        game_started = True
        
    broadcast_tcp(f"START TCP_PORT {TCP_PORT} UDP_PORT {UDP_PORT} TIME {TIME_PER_Q} ROUNDS {NUM_QUESTIONS}")

    
    usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    usock.bind(("0.0.0.0", UDP_PORT))
    usock.settimeout(0.5)

    for qi in range(1, NUM_QUESTIONS + 1):
        q, opts, correct = random.choice(QUESTIONS)
        broadcast_tcp(format_question(qi, q, opts))

        received = {}  # username -> 'a'/'b'/'c'/'d'
        deadline = time.time() + TIME_PER_Q

        while time.time() < deadline:  # keep waiting until time runs out
    try:
        data, uaddr = usock.recvfrom(1024)  # receive data from the client
    except socket.timeout:  # if no data is received in time, skip and continue
        continue

    try:
        s = data.decode().strip()  # decode and clean the received data
        if "|" not in s:  # ensure the data has both username and answer
            continue
        
        uname, ans = s.split("|", 1)  # split username and answer
        uname, ans = uname.strip(), ans.strip().lower()  # clean up spaces and standardize answer
        
        with lock:  # lock to safely modify shared data
            if uname not in players:  # skip if the player isn't in the game
                continue
            if uname in received:  # skip if the player already answered
                continue
            
            received[uname] = ans  # save the player answer
            players[uname]['udp_addr'] = uaddr  # store the player's UDP address
        
        # provide feedback whether the answer is correct or not
        feedback = f"FEEDBACK {uname} " + ("Correct" if ans == correct else "Wrong")
        usock.sendto((feedback + "\n").encode(), uaddr)  # send back to the player
    except: 
        continue  # skip any errors and continue waiting for valid data

                continue

     ################calculat point
        with lock:
            for uname, info in players.items():
                if uname in received and received[uname] == correct:
                    info['score'] += 1

        # broadcast grades
        lines = ["SCORES:"]
        with lock:
            for uname in sorted(players.keys()):
                lines.append(f"{uname}: {players[uname]['score']}")
        broadcast_tcp("\n".join(lines))

    # final result
    with lock:
        best = max((info['score'] for info in players.values()), default=0)
        winners = [u for u, info in players.items() if info['score'] == best]
    lines = ["Final Results:"]
    with lock:
        for uname in sorted(players.keys()):
            lines.append(f"{uname}: {players[uname]['score']} points")
    lines.append("Winner: " + (", ".join(winners) if winners else "None"))
    lines.append("BYE")
    broadcast_tcp("\n".join(lines))

   #close
    with lock:
        for info in players.values():
            try: info['conn'].close()
            except: pass
    usock.close()

def main():

    tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tsock.bind(("0.0.0.0", TCP_PORT))
    tsock.listen(8)
    print(f"[SERVER] TCP on {TCP_PORT}, UDP on {UDP_PORT}")

    threading.Thread(target=wait_and_start, daemon=True).start()

    while True:
        try:
            conn, addr = tsock.accept()
        except:
            break
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
