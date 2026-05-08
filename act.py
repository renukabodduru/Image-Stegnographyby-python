import tkinter as tk
from tkinter import messagebox, filedialog #which is used to open and save files
from PIL import Image, ImageTk  #image processing and placing it in tkinter
import json             #storing and loading data
import os         #file sysytem operations
import hashlib       #securing hashing passwords using SHA-256 algorithm

# File to store user data
USER_DATA_FILE = "users.json"

# Hashing the password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()     #this takes the password as input
                                                             #hashes it using SHA-256 algorithmand returns hexadecimal representation of hash

# Load user data from JSON file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Save user data to JSON file
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

# User registration function
def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Registration", "Please enter both username and password.")
        return

    users = load_user_data()

    if username in users:
        messagebox.showwarning("Registration", "Username already exists.")
        return

    users[username] = hash_password(password)
    save_user_data(users)
    messagebox.showinfo("Registration", "Registration successful!")
    root.destroy()
    main_application()

# User login function
def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Login", "Please enter both username and password.")
        return

    users = load_user_data()

    if username in users and users[username] == hash_password(password):
        messagebox.showinfo("Login", "Login successful!")
        root.destroy()
        main_application()
    else:
        messagebox.showwarning("Login", "Invalid username or password.")

# Create login window
def login_window():
    global entry_username, entry_password, root #variables (global)
    root = tk.Tk()     #intializing window
    root.geometry("900x600") #window size
    root.title("Login form") #title of the window

    
    #these are the label for heading
    tk.Label(root, text="Enter your details",font=("Helvetica",16,"underline")).place(x=370,y=150)
   
    #these are the positioning for the label fields 
    tk.Label(root, text="Username",font=("Georgia",12)).place(x=290,y=200)
    tk.Label(root, text="Password",font=("Georgia",12)).place(x=290,y=250)

#these give the input fields for username and password fields
    entry_username = tk.Entry(root,font=("Courier",12),width=20,bd=5,relief="groove")
    entry_password = tk.Entry(root,font=("Courier",12),width=20,bd=5,relief="groove",show="•")
  
#these are the boxes for username and password fields positioning
    entry_username.place(x=380,y=200)
    entry_password.place(x=380,y=250)

#these are the login and register button positioning
    tk.Button(root, text="Login", command=login_user,font=("verdana",12),relief="raised",bd=6,width=12).place(x=380,y=320)
    tk.Button(root, text="Register", command=register_user,font=("verdana",12),relief="raised",bd=6,width=12).place(x=380,y=380)



    root.mainloop() #this runs the continuos events that are held from user

## Encoder function
def encode_message():     #encoding function starts here
    global img            #img variable
    message = entry_message.get("1.0",tk.END.strip())   ##multiline text   #we are getting the message that is given in the entry field
    passkey = entry_passkey.get()   #we are gettingthe passkey that is given in the entry field

    if not img:
        messagebox.showwarning("Encoder", "Please load an image first.")        #shows a pop up box if its not given an image
        return
    if not message or not passkey:
        messagebox.showwarning("Encoder", "Please enter both message and passkey.") #shows a pop up box if we not entered msg or passkey
        return

    binary_message = ''.join([format(ord(i), "08b") for i in passkey + message])               
    binary_message += "1111111111111110"  # Terminator to indicate end of message

    data_index = 0
    pixel_data = img.load()

    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixel_data[x, y]
            if data_index < len(binary_message):
                r = int(format(r, "08b")[:-1] + binary_message[data_index], 2)
                data_index += 1
            if data_index < len(binary_message):
                g = int(format(g, "08b")[:-1] + binary_message[data_index], 2)
                data_index += 1
            if data_index < len(binary_message):
                b = int(format(b, "08b")[:-1] + binary_message[data_index], 2)
                data_index += 1
            pixel_data[x, y] = (r, g, b)
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break

    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if filename:
        img.save(filename)
        messagebox.showinfo("Encoder", "Message encoded and image saved successfully.")

# Decoder function in a separate window
def decode_window():
    decode_root = tk.Toplevel()
    decode_root.title("Decoder")
    decode_root.geometry("900x600")  # Set the size of the window to 400x300 pixels


    def decode_message():
        global img
        passkey = entry_decode_passkey.get()                                #getting a passkey in decode session 

        if not img:
            messagebox.showwarning("Decoder", "Please load an image first.")                  #warning for not loading the image in decoder
            return
        if not passkey:
            messagebox.showwarning("Decoder", "Please enter the passkey.")                    #warning for not loading the passkey in decode session
            return

        binary_message = ""
        pixel_data = img.load()

        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixel_data[x, y]
                binary_message += format(r, "08b")[-1]
                binary_message += format(g, "08b")[-1]
                binary_message += format(b, "08b")[-1]

        all_bytes = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
        decoded_message = ""
        current_passkey = ""

        terminator="11111110"
        
        is_terminator_found=False
          
        for byte in all_bytes:
            if byte==terminator:
                is_terminator_found=True
                break
            decoded_message+=chr(int(byte,2))

            if is_terminator_found:
                messagebox.showerror("decoder","the terminatorwas not found.The msg may be corrupted orthe wrong pass key was used")
                return
        # for byte in all_bytes:
        #     if decoded_message[-8:] == "11111110":  # Terminator
        #         break
        #     decoded_message += chr(int(byte, 2))

        if decoded_message.startswith(passkey):
            entry_decoded_message.delete("1.0", tk.END)
            entry_decoded_message.insert("1.0", decoded_message[len(passkey):-8])
        else:
            messagebox.showerror("Decoder", "Invalid passkey!")

    
    tk.Label(decode_root, text="Passkey:").grid(row=0, column=0)
    entry_decode_passkey = tk.Entry(decode_root)
    entry_decode_passkey.grid(row=0, column=1)
    
   
    tk.Button(decode_root, text="Load Image", command=load_image,font=("verdana",8),relief="raised",width=12).grid(row=1, column=0, columnspan=2,padx=5,pady=5)

    tk.Label(decode_root, text="Decoded Message:").grid(row=2, column=0)
    entry_decoded_message = tk.Text(decode_root,width=20,height=10)
    entry_decoded_message.grid(row=2, column=1)

    tk.Button(decode_root, text="Decode", command=decode_message).grid(row=3, column=0, columnspan=2)

    decode_root.mainloop()

# Load image function
def load_image():
    global img, img_display
    filename = filedialog.askopenfilename()
    if filename:
        img = Image.open(filename)
        img = img.convert("RGB")
        img_display = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_display)

# Main application function
def main_application():
    global img, img_display, entry_message, entry_passkey, canvas
    app_root = tk.Tk()
    app_root.title("Image Steganography")
    app_root.geometry("900x600")  # Set the width and height of the window

    tk.Label(app_root,text="encoder")

    frame = tk.Frame(app_root)
    frame.pack()

    canvas = tk.Canvas(frame, width=500, height=300)
    canvas.pack()

    tk.Button(frame, text="Load Image", command=load_image).pack(padx=10,pady=10)

    tk.Label(frame, text="Passkey:").pack(padx=10,pady=10)
    entry_passkey = tk.Entry(frame)
    entry_passkey.pack()

    tk.Label(frame, text="Message:").pack(padx=10,pady=10)
    entry_message = tk.Text(frame,height=4,width=30)
    entry_message.pack()

    tk.Button(frame, text="Encode", command=encode_message).pack(padx=10,pady=10)
    tk.Button(frame, text="Decode", command=decode_window).pack(padx=10,pady=10)

    app_root.mainloop()

# Start the login window
login_window()
