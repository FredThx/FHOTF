import PySimpleGUIQt as sg
layout = [
    [sg.Text("Hotfolder path : "), sg.InputText(key='path',default_text = 'e:\\hotfolder'),sg.FolderBrowse(initial_folder = 'e:\\hotfolder')],
    [sg.Text("Smtp :")],
    [sg.Text('   Host     : '), sg.InputText(key = 'smtp_host')],
    [sg.Text('   Port     :'),sg.InputText(key = 'smtp_port')],
    [sg.Text('   Sender   :'), sg.InputText(key = 'smtp_user')],
    [sg.Text('   Password :'), sg.InputText(key='smtp_password', password_char="*")],
    [sg.Cancel(),sg.OK()] ]

event, values = sg.Window('Enter a number example', layout).Read()
print(event)
print(values)


'''
FolderBrowse(button_text="Browse",
    target=(555666777, -1),
    initial_folder=None,
    tooltip=None,
    size=(None, None),
    auto_size_button=None,
    button_color=None,
    disabled=False,
    change_submits=False,
    enable_events=False,
    font=None,
    pad=None,
    key=None,
    metadata=None)
'''
