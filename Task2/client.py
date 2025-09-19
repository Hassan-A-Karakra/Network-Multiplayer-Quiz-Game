import socket
import time

# ========================= connect server ============================
SERVER_IP = "127.0.0.1" 
STUDENT_ID = "1220501" 
TCP_PORT = int(STUDENT_ID[-3:]) + 3000 #####
UDP_PORT = int(STUDENT_ID[:3]) + 6000
USERNAME = input("Enter username: ").strip()


# This function receives data from the socket
def recv_lines(sock):
    try:
        data = sock.recv(4096)
        if not data:
            return []
        return data.decode(errors="ignore").splitlines()
    except:
        return []

#-------------------------- This method connects to the server using TCP --------------------------------
def main():
    # TCP connect & JOIN
    tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tsock.connect((SERVER_IP, TCP_PORT))
    print("[TCP] Connected.")
    print(tsock.recv(1024).decode(), end="")   
    tsock.sendall(f"JOIN {USERNAME}\n".encode())
    print(tsock.recv(1024).decode(), end="")

    # UDP skt for answres + feed back
    usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    usock.bind(("", 0))
    usock.settimeout(0.5)

    game_over = False
    buffer = ""

    while not game_over:
        lines = recv_lines(tsock)
        for line in lines:
            if not line:
                continue
            print(line)
            if line.startswith("START "):
              
                pass
            elif line.startswith("Q"):
               
                print(line)  
                continue
            elif line.startswith("SEND ANSWER VIA UDP"):
             
                choice = input("Your answer (a/b/c/d): ").strip().lower()
                if choice not in ("a", "b", "c", "d"): ### Select the answer
                    print("Invalid answer. Sending 'x' as incorrect answer.")
                    choice = "x" 
                msg = f"{USERNAME}|{choice}".encode()
                usock.sendto(msg, (SERVER_IP, UDP_PORT))


                t_end = time.time() + 2.0
                while time.time() < t_end:
                    try:
                        fb, _ = usock.recvfrom(1024)
                        print(fb.decode().strip())
                        break
                    except socket.timeout:
                        print("No feedback received, retrying...") 
                        continue

            elif line.startswith("SCORES:"):
               
                pass
            elif line.startswith("Final Results:"): #display the final scores and closes the connections
                game_over = True

  
    more = recv_lines(tsock)
    for line in more:
        print(line)

    tsock.close()
    usock.close()
    print("[CLIENT] Good Bye and thank you sharing in this game..")

#********************* Check if this script is being run **************************************
if __name__ == "__main__":
    main()
