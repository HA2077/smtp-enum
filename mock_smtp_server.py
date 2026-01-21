import socket
import sys
import os

# A Smart Mock SMTP server that simulates 250 (Found), 252 (Ambiguous), and 550 (Unknown)
# REQUIRES SUDO/ROOT privileges.
def start_server(host='127.0.0.1', port=25):
    # Check if running as root
    if os.geteuid() != 0:
        print(f"[-] Error: Binding to port {port} requires root privileges.")
        print(f"    Please run: sudo python3 {sys.argv[0]}")
        sys.exit(1)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        
        print(f"\n[+] Mock SMTP Server running on {host}:{port}")
        print("[!] Press Ctrl+C to stop...\n")

        while True:
            try:
                client, addr = server.accept()
                print(f"[>] Connection received from {addr[0]}")

                client.send(b"220 SmartMock Server Ready\r\n")

                while True:
                    data = client.recv(1024)
                    if not data: break
                    
                    decoded = data.decode('utf-8', errors='ignore').strip()
                    if not decoded: continue

                    print(f"    [Received]: {decoded}")

                    if decoded.upper().startswith("HELO") or decoded.upper().startswith("EHLO"):
                        client.send(b"250 Hello\r\n")
                    
                    elif decoded.upper().startswith("VRFY"):
                        parts = decoded.split(" ")
                        user = parts[-1].strip() if len(parts) > 1 else ""
                        
                        if user.lower() in ['admin', 'root', 'Hassan']:
                            client.send(f"250 2.0.0 {user} User found\r\n".encode())
                            print(f"    [+] Responded 250 for '{user}'")
                            
                        elif user.lower() in ['support', 'developer']:
                            client.send(f"252 2.0.0 {user} Cannot VRFY, but will accept\r\n".encode())
                            print(f"    [~] Responded 252 for '{user}'")
                            
                        else:
                            client.send(b"550 5.1.1 User unknown\r\n")
                            print(f"    [-] Responded 550 for '{user}'")
                        
                    elif decoded.upper().startswith("QUIT"):
                        client.send(b"221 Bye\r\n")
                        break
                    else:
                        client.send(b"250 OK\r\n")
                        
                client.close()
                print("[<] Connection closed\n")

            except Exception as e:
                print(f"[-] Client Error: {e}")

    except KeyboardInterrupt:
        print("\n[!] Stopping server...")
        server.close()
        sys.exit()
    except Exception as e:
        print(f"\n[-] Fatal Error: {e}")

if __name__ == "__main__":
    start_server()