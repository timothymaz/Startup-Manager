import os
import tkinter as tk
from tkinter import ttk, filedialog
import winreg
from PIL import Image, ImageTk
from ttkthemes import ThemedTk

# Function to load startup items
def load_startup_items():
    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    startup_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)

    startup_items = []
    i = 0
    while True:
        try:
            name, value, value_type = winreg.EnumValue(startup_key, i)
            startup_items.append((name, value, True))
            i += 1
        except OSError:
            break

    winreg.CloseKey(startup_key)
    return startup_items

# Function to load the icons of all the startup items
def load_startup_icons(startup_items):
    icons = {}
    for name, path, status in startup_items:
        icon = get_exe_icon(path)
        icons[name] = icon
    return icons

# Function to populate the treeview
def populate_treeview(treeview, filter_text=None, icons=None):
    treeview.delete(*treeview.get_children())
    startup_items = load_startup_items()

    if icons is None:
        icons = load_startup_icons(startup_items)

    for name, path, status in startup_items:
        if not filter_text or filter_text.lower() in name.lower():
            # Get the file name and icon
            file_name = get_exe_path(name)
            icon = icons.get(name)
            treeview.insert('', 'end', text=file_name, image=icon, values=(path, status))

# Function to get the path of an executable
def get_exe_path(name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{}.exe'.format(name))
        path = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
        return os.path.abspath(path)
    except:
        return None

# Function to get the icon of an executable
def get_exe_icon(path, size=(16, 16)):
    try:
        img = Image.open(path)
        img.thumbnail(size)
        icon = ImageTk.PhotoImage(img)
    except:
        icon = None

    return icon

# Function to update the status bar
def update_status_bar(treeview):
    status_bar_text.set(f"Total items: {len(treeview.get_children())}")

# Function to toggle enable/disable
def toggle_status(item_id):
    item = treeview.item(item_id)
    name = item['text']
    path, status = item['values']
    new_status = not status
    item['values'] = (path, new_status)

    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    startup_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)

    if new_status:
        winreg.SetValueEx(startup_key, name, 0, winreg.REG_SZ, path)
    else:
        winreg.DeleteValue(startup_key, name)

    winreg.CloseKey(startup_key)

# Function to add a new startup item
def add_startup_item():
    file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
    
    if not file_path:
        return

    name = file_path.split("\\")[-1].split(".")[0]
    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    startup_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(startup_key, name, 0, winreg.REG_SZ, file_path)
    winreg.CloseKey(startup_key)

# Function to remove a startup item
def remove_startup_item(name):
    key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    startup_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
    winreg.DeleteValue(startup_key, name)
    winreg.CloseKey(startup_key)

# Function to prioritize a startup item
def prioritize_startup_item(item_id):
    treeview.move(item_id, '', 0)

# Function to show the context menu
def show_context_menu(event):
    item_id = treeview.identify_row(event.y)
    if not item_id:
        return

    treeview.selection_set(item_id)
    context_menu.post(event.x_root, event.y_root)

# Function to open the settings window
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    # Create a frame for the theme setting
    theme_frame = tk.Frame(settings_window)
    theme_frame.pack(pady=10)

    theme_label = tk.Label(theme_frame, text="Theme:")
    theme_label.pack(side='left')

    theme_var = tk.StringVar()
    theme_var.set("light")

    theme_dropdown = ttk.Combobox(theme_frame, textvariable=theme_var, values=("light", "dark"), state="readonly")
    theme_dropdown.pack(side='left')

    # Bind the theme change event
    theme_dropdown.bind('<<ComboboxSelected>>', lambda event: change_theme(theme_var.get()))

    # Add a close button to the settings window
    close_button = tk.Button(settings_window, text="Close", command=settings_window.destroy)
    close_button.pack(pady=10)

# Function to change the theme
def change_theme(theme):
    if theme == 'light':
        root.config(bg='#ffffff')
        toolbar.config(bg='#f0f0f0')
        status_bar.config(bg='#f0f0f0')
    elif theme == 'dark':
        root.config(bg='#2e2e2e')
        toolbar.config(bg='#434343')
        status_bar.config(bg='#434343')

#Create the main window

root = ThemedTk(theme="radiance")
root.title('Startup Manager')
#Create the toolbar

toolbar = tk.Frame(root)
toolbar.pack(side='top', fill='x')

refresh_button = ttk.Button(toolbar, text='Refresh', command=lambda: populate_treeview(treeview))
refresh_button.pack(side='left')

add_button = ttk.Button(toolbar, text='Add', command=add_startup_item)
add_button.pack(side='left')

remove_button = ttk.Button(toolbar, text='Remove', command=lambda: remove_startup_item(treeview.item(treeview.focus())['text']))
remove_button.pack(side='left')

prioritize_button = ttk.Button(toolbar, text='Prioritize', command=lambda: prioritize_startup_item(treeview.focus()))
prioritize_button.pack(side='left')

search_label = ttk.Label(toolbar, text="Search:")
search_label.pack(side='left', padx=5)

search_var = tk.StringVar()

search_entry = ttk.Entry(toolbar, textvariable=search_var)
search_entry.pack(side='left')

search_button = ttk.Button(toolbar, text='Search', command=lambda: populate_treeview(treeview, filter_text=search_var.get()))
search_button.pack(side='left')
#Add a settings button to the toolbar

settings_button = ttk.Button(toolbar, text='Settings', command=open_settings)
settings_button.pack(side='right')
#Create the treeview

treeview = ttk.Treeview(root, columns=('Path', 'Status'), show='headings')
treeview.heading('Path', text='Path')
treeview.heading('Status', text='Enabled')
treeview.pack(fill='both', expand=True)
#Bind double-click event to toggle enable/disable

treeview.bind('<Double-1>', lambda event: toggle_status(treeview.focus()))
#Bind right-click event to show context menu

treeview.bind('<Button-3>', show_context_menu)
#Load the startup items

populate_treeview(treeview)
#Create the status bar

status_bar = ttk.Frame(root, relief='sunken')
status_bar.pack(side='bottom', fill='x')

status_bar_text = tk.StringVar()
status_label = ttk.Label(status_bar, textvariable=status_bar_text, anchor='w')
status_label.pack(side='left')
#Update the status bar

update_status_bar(treeview)
#Create the context menu

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label='Enable/Disable', command=lambda: toggle_status(treeview.focus()))
context_menu.add_command(label='Remove', command=lambda: remove_startup_item(treeview.item(treeview.focus())['text']))
context_menu.add_command(label='Prioritize', command=lambda: prioritize_startup_item(treeview.focus()))
#Add the icon

icon = ImageTk.PhotoImage(Image.open("startup_icon.png"))
root.iconphoto(True, icon)
#Run the main loop

root.mainloop()