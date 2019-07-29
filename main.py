import kivy
import paramiko
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image


Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 100)
Config.set('graphics', 'top',  100)
Config.set('graphics', 'resizable', True)
from kivy.core.window import Window

class configurFile:
    def __init__(self):
        self.file_name = "configur.txt"
        self.host_ips = []
        self.log_path = ""
        self.parameter_path = []
    def read_file(self):
        f=open(self.file_name,"r")
        self.host_ips.clear()
        self.parameter_path.clear()
        self.log_path=""

        text=f.read()
        text=text.split("\n")
        for items in text:
            line=items.split(":")
            if line[0] == "host":
                for i in range(1,len(line)):
                    self.host_ips.append(line[i])
            if line[0] == "logpath":
                self.log_path=line[1]
            if line[0] == "parameterpath":
                for i in range(1,len(line)):
                    self.parameter_path.append(line[i])
        f.close()
    def edit_file(self,choice,data):
        f=open(self.file_name,"r")
        new_data=[]
        old_data=f.readlines()
        f.close()
        f=open(self.file_name,"w")
        for items in old_data:
            if choice in items:
                new_data.append(items.strip()+":"+data+"\n")
            else:
                new_data.append(items)
        print(new_data)
        f.writelines(new_data)
        f.close()

    def delete_data(self,data):
        f = open(self.file_name, "r")
        exist=0
        new_data = []
        old_data = f.readlines()
        f.close()
        f = open(self.file_name, "w")
        for items in old_data:
            if data in items:
                items=items.replace(":"+data,'')
                exist=1

            new_data.append(items)

        f.writelines(new_data)
        f.close()
        return exist





class Ssh_Util:
    "Class to connect to remote server"

    def __init__(self):
        self.file=configurFile()
        self.ssh_output = None
        self.ssh_error = None
        self.client = None
        self.host = None
        self.username = None
        self.password = None
        self.port = 22
        self.sftp = None
        self.transport = None

    def connect(self,host_name,user_name,user_passw):
        self.file.read_file()
        self.client= paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host=host_name
        self.username=user_name
        self.password=user_passw
        self.transport = paramiko.Transport((self.host,self.port))
        self.transport.connect(username=self.username,password=self.password)
        self.sftp=paramiko.SFTPClient.from_transport(self.transport)

        try:
            self.client.connect(hostname=self.host, username=self.username, password=self.password)
            #print("Connected, welcome " + self.username + " !")
            return 1
        except paramiko.ssh_exception.AuthenticationException as e:
            #print ( "Authentication Fault")
            return 2
        except paramiko.ssh_exception.BadHostKeyException as e:
            #print("Host Error")
            return 3
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            #print("Connection error")
            return 4
        except paramiko.ssh_exception.SSHException as e:
            return 4
        except paramiko.ssh_exception.ChannelException as e:
            return 4
        except:
            return 4

    def execute_command(self, command):
        self.ssh_output = None
        try:
            print("Executing command -->"+str(command))
            stdin, stdout, stderr = self.client.exec_command(command)
            self.ssh_output = stdout.read()
            self.ssh_error = stderr.read()
            if self.ssh_error:
                print("Problem occurred while running command:" + command + " The error is " + self.ssh_error.decode("utf-8"))
            else:
                print ("Command execution completed successfully")


        except paramiko.SSHException:
            print ("Failed to execute the command!"+command)

        except:
            print("olmadı")


class LoginScreen(Screen):
    ip_buttons=[]
    first_select_press=True
    file=configurFile()
    def host_list(self):
        if self.first_select_press:
            self.file.read_file()
            for items in self.file.host_ips:
                tempor_btn = Button(text=items, id=str(items), size_hint=(1, 0.2),on_press=self.host_click)
                self.ip_buttons.append(tempor_btn)
                self.manager.ids.login.ids.select_box.add_widget(tempor_btn)
                self.first_select_press = False
        else:
            self.remove_widgets()


    def host_click(self,instance):
        self.manager.screens[1].host=instance.text
        self.manager.current = "main"
    def remove_widgets(self):
        for items in self.ip_buttons:
            self.manager.ids.login.ids.select_box.remove_widget(items)
        self.first_select_press = True
        self.ip_buttons.clear()


class MainScreen(Screen):
    user=ObjectProperty(None)
    password=ObjectProperty(None)
    host=""
    result=ObjectProperty(None)
    output=ObjectProperty(None)
    commandbox=ObjectProperty(None)
    buttons=[]
    log_tail_text=""
    first_btn_press = True
    first_script_press = True
    log_number=0
    script_number=0
    scripts=[]
    ssh=Ssh_Util()
    file=configurFile()
    file.read_file()
    def connect_btn(self):
        validation=self.ssh.connect(str(self.host),str(self.user.text),str(self.password.text))
        if validation == 1:
            self.result.text = "Connected, welcome " + self.user.text + " !"
        if validation == 2:
            self.result.text = "Authentication Fault"
        if validation == 3:
            self.result.text = "Host Error"
        if validation == 4:
            self.result.text = "Connection error"
    def disconnect(self):
        if self.ssh.client:
            self.ssh.client.close()
            self.result.text="Not connected"
            self.ssh.client=None

    def apply_btn(self):
        if self.ssh.client:
            commands = self.commandbox.text
            try:
                self.ssh.execute_command(commands)
                print(self.ssh.ssh_output)
                self.output.text = self.ssh.ssh_output
            except:
                pass
    def log_btn(self):
        if self.ssh.client:
            commands = "ls " + self.file.log_path  # DIRECTORY
            log_names = []
            first_seperation = []

            self.ssh.execute_command(commands)
            self.output.text = self.ssh.ssh_output
            first_seperation = self.output.text.split("\n")
            for items in first_seperation:
                if ".log" in items:
                    log_names.append(items)

            self.log_number = len(log_names)

            for i in range(self.log_number):
                print(log_names[i])
            if self.first_btn_press:
                for i in range(self.log_number):
                    second_seperation = log_names[i].split("/")
                    third_separation = second_seperation[2].split("_")
                    tempor_btn = Button(text=third_separation[2], id=log_names[i], size_hint=(1, 1),
                                        on_press=self.log_open)
                    self.buttons.append(tempor_btn)
                    self.manager.ids.another.ids.box.add_widget(tempor_btn)
                    self.first_btn_press = False




    def log_open(self, instance):
        if self.ssh.client:
            try:
                path = instance.id.strip()
                self.ssh.execute_command("tail -20 " + path)
                self.log_tail_text = self.ssh.ssh_output.decode("utf-8")
                self.manager.screens[2].log_tail.text = self.log_tail_text

            except:
                print("error")

    def scripts_btn(self):
        if self.ssh.client:
            command = "ls"
            first_separation = []
            script_names = []
            try:
                self.ssh.execute_command(command)
                self.output.text = self.ssh.ssh_output

                first_separation = self.output.text.split("\n")
                for items in first_separation:

                    if ".sh" in items:
                        script_names.append(items)

                self.script_number = len(script_names)

                if self.first_script_press:
                    for i in range(self.script_number):
                        tempor_btn = Button(text=script_names[i], id=str(i), size_hint=(1, 1), on_press=self.show_script)
                        run_btn = Button(text="Run",id=script_names[i],size_hint=(1,1),on_press=self.run_script)
                        self.scripts.append(tempor_btn)
                        self.manager.ids.scriptscreen.ids.script_box.add_widget(tempor_btn)
                        self.manager.ids.scriptscreen.ids.script_run_box.add_widget(run_btn)
                        self.first_script_press = False
            except:
                print("error")

    def show_script(self, instance):
        self.ssh.execute_command("cat "+instance.text)

        self.manager.screens[3].script_show_label.text=self.ssh.ssh_output.decode("utf-8")
    def run_script(self,instance):
        try:
            self.ssh.execute_command("./"+instance.id)
            if self.ssh.ssh_error:
                self.manager.screens[3].exe_label.text = self.ssh.ssh_error.decode("utf-8")
            else:
                self.manager.screens[3].exe_label.text = "Execution successful"
        except:
            self.manager.screens[3].exe_label.text=self.ssh.ssh_error.decode("Execution failed ")




class AnotherScreen(Screen):
    log_tail=ObjectProperty(None)
    def button__refresh(self):
        remove_list=self.manager.screens[1].buttons
        for items in remove_list:
            self.manager.ids.another.ids.box.remove_widget(items)
        self.manager.screens[1].first_btn_press=True


class ScriptScreen(Screen):
    script_show_label=ObjectProperty(None)
    exe_label=ObjectProperty(None)




class PassageScreen(Screen):
    parameter_label=ObjectProperty(None)
    first_parameter_press=True
    firs_edit_press=True
    parameter_path=""
    save_widgets=[]
    parameter_file_choice=-1
    parameter_button_list=[]
    edit_button_list=[]
    file=configurFile()
    file.read_file()

    def parameter_btn(self,id):
        thissh = self.manager.screens[1].ssh

        if id == "10":
            self.parameter_file_choice=0 #NAME
            thissh.execute_command("ls "+self.file.parameter_path[0]+"/*_parameter.ini")  #DIRECTORY 2
            if self.first_parameter_press == False:
                    for items in self.parameter_button_list:
                        self.manager.ids.passagescreen.ids.para_box.remove_widget(items)
                    self.manager.screens[4].first_parameter_press = True

                    for items in self.edit_button_list:
                        self.manager.ids.passagescreen.ids.edit_box.remove_widget(items)

        if id == "11":
            self.parameter_file_choice=1 #NAME
            thissh.execute_command("ls "+self.file.parameter_path[1]+"/*_parameter.ini")  #DIRECTORY 3
            if self.first_parameter_press == False:
                for items in self.parameter_button_list:
                    self.manager.ids.passagescreen.ids.para_box.remove_widget(items)
                self.manager.screens[4].first_parameter_press = True

                for items in self.edit_button_list:
                    self.manager.ids.passagescreen.ids.edit_box.remove_widget(items)

        outputtext=thissh.ssh_output.decode("utf-8")
        errortext=thissh.ssh_error.decode("utf-8")
        print(errortext)
        print(outputtext)
        firstseparation=outputtext.split("\n")

        if self.first_parameter_press:
            for i in range(len(firstseparation)-1):
                secondseparation = firstseparation[i].split("/")
                thirdseparation=secondseparation[3].split("_")
                tempor_button = Button(text=thirdseparation[0], id=str(firstseparation[i]), size_hint=(1, 1),on_press=self.show_parameter)
                tempor_edit_button = Button(text="Edit", id=str(firstseparation[i]), size_hint=(1, 1),on_press=self.edit)
                self.manager.ids.passagescreen.ids.para_box.add_widget(tempor_button)
                self.manager.ids.passagescreen.ids.edit_box.add_widget(tempor_edit_button)
                self.edit_button_list.append(tempor_edit_button)
                self. parameter_button_list.append(tempor_button)
                self.first_parameter_press= False

    def show_parameter(self,instance):
        ssh=self.manager.screens[1].ssh
        path = instance.id.strip()
        ssh.execute_command("cat " +path)    #DIRECTORY 4
        self.parameter_label.text = ssh.ssh_output.decode("utf-8")
        self.refresh_widgets()


    def edit(self,instance):
        if self.firs_edit_press:
            ssh = self.manager.screens[1].ssh
            path = instance.id.strip()
            self.parameter_path=path
            already_text = self.parameter_label.text
            tempor_text = TextInput(text=already_text, id="edit_text", size_hint=(0.5, 1))
            tempor_button = Button(text="S\nA\nV\nE", id="save_btn", size_hint=(0.1, 1),on_press=self.save_text)
            self.manager.ids.passagescreen.ids.save_box.add_widget(tempor_text)
            self.manager.ids.passagescreen.ids.save_box.add_widget(tempor_button)
            self.save_widgets.append(tempor_button)
            self.save_widgets.append(tempor_text)
            self.firs_edit_press=False

    def refresh_widgets(self):
        if self.save_widgets:
            for items in self.save_widgets:
                self.manager.ids.passagescreen.ids.save_box.remove_widget(items)
            self.save_widgets.clear()
            self.firs_edit_press = True
    def save_text(self,instance):
        if self.save_widgets:
            ssh = self.manager.screens[1].ssh
            f = ssh.sftp.open(self.parameter_path, "wb")
            f.write(self.save_widgets[1].text)
            f.close()

class SettingScreen(Screen):
    new_host_input=ObjectProperty(None)
    f=configurFile()
    def add_host(self):
        isitip=True
        if ":" in self.new_host_input.text:
            self.new_host_input.text="Invalid Syntax"
            isitip=False
        for chars in self.new_host_input.text:
            if chars.isalpha():
                isitip=False
                self.new_host_input.text="Invalid Syntax"
        if isitip:
            self.f.edit_file(choice="host",data=self.new_host_input.text)
            self.new_host_input.text="Success !"
    def delete_data(self):
        data=self.new_host_input.text
        exist=self.f.delete_data(data)
        if exist == 1:
            self.new_host_input.text="Succes !"
        else:
            self.new_host_input.text="No match"


class ScreenManager(ScreenManager):
    pass


kv=Builder.load_file("my.kv")


class MyApp(App): # <- Main Class
    def build(self):
        return kv


if __name__ == "__main__":
    MyApp().run()