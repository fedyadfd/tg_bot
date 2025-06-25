from tkinter import*
import time
from playsound import playsound


class Player:
    def __init__(self,x1,y1,x2,y2,color):
        self.id=canvas.create_rectangle(x1,y1,x2,y2,fill=color)
        self.y = 0
        self.speed = 3
        self.key_up = None
        self.key_down = None
        self.initial_cords = (x1, y1, x2, y2)
        self.final_cords = None

    def draw(self):
        canvas.move(self.id,0,self.y)
        _,y,_,y1 = canvas.coords(self.id)
        if y <= 0:
            self.y = 0
            canvas.coords(self.id,self.initial_cords)
        elif y1 >= 600:
            self.y = 0
            canvas.coords(self.id,self.final_cords)

    def move(self,event):
        if event.keysym == self.key_up:
            self.y = -self.speed
        elif event.keysym == self.key_down:
            self.y = self.speed
    def stop(self,event):
        if event.keysym in (self.key_up,self.key_down):
            self.y = 0




class Player1(Player):
    def __init__(self):
        super().__init__(30,10,40,90,"white")
        self.key_up = "w"
        self.key_down = "s"
        self.final_cords = (30,510,40,590)


class Player2(Player):
    def __init__(self):
        super().__init__(760, 10, 770, 90,"white")
        self.key_up = "Up"
        self.key_down = "Down"
        self.final_cords = (760, 510, 770, 590)


class Ball():
    def __init__(self):
        self.id = canvas.create_oval(40,20,70,50, fill="white")
        self.x = 3
        self.y = 3
    def draw(self):
        global score
        canvas.move(self.id,self.x,self.y)
        bx,by,bx1,by1 = canvas.coords(self.id)
        x1,y1,x11,y11 = canvas.coords(pong1.id)
        x2,y2,x22,y22 = canvas.coords(pong2.id)
        if by <= 0 or by1 >= 600:
            self.y = -self.y
        if by > y1-5 and by1 < y11+5 and bx <= x11:
            score += 1
            canvas.itemconfig(score_gui, text=f"счёт: {score}")
            self.x -= 0.25
            playsound("pong.mp3", block=False)
            self.x =- self.x
            pong1.speed += 0.25
        if by > y2-5 and by1 < y22+5 and bx1 >= x2:
            score += 1
            canvas.itemconfig(score_gui,text = f"счёт: {score}")
            self.x += 0.25
            playsound("pong.mp3", block=False)
            self.x =- self.x
            pong2.speed += 0.25
        if bx <= 0 or bx1 >= 800:
            return True

root = Tk()
root.geometry("800x600")
canvas = Canvas(root,width=800,height=600,bg="black")
canvas.pack()

pong1 = Player1()
pong2 = Player2()
ball = Ball()

canvas.bind_all(f"<KeyPress-{pong1.key_up}>",pong1.move)
canvas.bind_all(f"<KeyPress-{pong1.key_down}>",pong1.move)
canvas.bind_all(f"<KeyRelease-{pong1.key_up}>",pong1.stop)
canvas.bind_all(f"<KeyRelease-{pong1.key_down}>",pong1.stop)

canvas.bind_all(f"<KeyPress-{pong2.key_up}>",pong2.move)
canvas.bind_all(f"<KeyPress-{pong2.key_down}>",pong2.move)
canvas.bind_all(f"<KeyRelease-{pong2.key_up}>",pong2.stop)
canvas.bind_all(f"<KeyRelease-{pong2.key_down}>",pong2.stop)

record_file = open("score.ini", "r+")
data = record_file.readline()
score = 0
if data == "":
    record = 0
    record_file.write(f"{record}")
    record_file.close()
else:
    record = int(data)

score_gui = canvas.create_text(390,20,text = f"счёт: {score}",fill="white",font=("Consolas",20))
canvas.create_text(390,50,text = f"рекорд: {record}",fill="white",font=("Consolas",20))

while True:
    try:
        root.update()
        root.update_idletasks()
        pong1.draw()
        pong2.draw()
        end = ball.draw()
        if end:
            break
        time.sleep(0.01)
    except TclError:
        print("твой рекорд защитан")
        break

record_file = open("score.ini", "r+")
a = record_file.readline()
if int(a) < score:
    record_file.truncate(0)
    record_file.seek(0)
    record_file.write(f"{score}")
record_file.close()
