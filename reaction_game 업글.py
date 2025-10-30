
import tkinter as tk
import random
import time

class ReactionGame:
    def __init__(self, master):
        self.master = master
        self.master.title("순발력 테스트 게임")
        self.master.geometry("400x400")

        # 게임 프레임
        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack()

        self.canvas = tk.Canvas(self.game_frame, width=400, height=350, bg="white")
        self.canvas.pack()

        self.message_label = tk.Label(self.game_frame, text="원이 초록색으로 바뀌면 클릭하세요!", font=("Helvetica", 14))
        self.message_label.pack(pady=10)

        # 결과 프레임
        self.result_frame = tk.Frame(self.master)
        self.result_label = tk.Label(self.result_frame, text="", font=("Helvetica", 16))
        self.result_label.pack(pady=20)

        self.retry_button = tk.Button(self.result_frame, text="재도전", command=self.retry_game)
        self.retry_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.exit_button = tk.Button(self.result_frame, text="게임 종료", command=self.master.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.circle = None
        self.start_time = None
        self.is_green = False
        self.game_over = False

        self.start_game()

    def start_game(self):
        self.game_over = False
        self.is_green = False
        self.result_frame.pack_forget()
        self.game_frame.pack()
        
        self.canvas.delete("all")
        self.circle = self.canvas.create_oval(150, 100, 250, 200, fill="red")
        self.canvas.tag_bind(self.circle, "<Button-1>", self.on_circle_click)
        
        self.schedule_color_change()

    def schedule_color_change(self):
        delay = random.randint(2000, 7000)  # 2초에서 7초 사이
        self.master.after(delay, self.change_color_to_green)

    def change_color_to_green(self):
        if self.game_over:
            return
        self.canvas.itemconfig(self.circle, fill="green")
        self.is_green = True
        self.start_time = time.time()

    def on_circle_click(self, event):
        if self.game_over:
            return

        self.game_over = True
        reaction_time = -1
        if self.is_green:
            reaction_time = (time.time() - self.start_time) * 1000  # ms
        
        self.show_results(reaction_time)

    def show_results(self, reaction_time):
        self.game_frame.pack_forget()
        self.result_frame.pack()

        result_text = ""
        if reaction_time < 0:
            result_text = "너무 빨리 클릭했습니다!"
        elif 0 <= reaction_time <= 100:
            result_text = f"신! ({reaction_time:.2f} ms)"
        elif 100 < reaction_time <= 200:
            result_text = f"프로게이머! ({reaction_time:.2f} ms)"
        elif 200 < reaction_time <= 300:
            result_text = f"고수! ({reaction_time:.2f} ms)"
        elif 300 < reaction_time <= 400:
            result_text = f"평균! ({reaction_time:.2f} ms)"
        else:
            result_text = f"조금 더 노력하세요! ({reaction_time:.2f} ms)"

        self.result_label.config(text=result_text)

    def retry_game(self):
        self.start_game()

if __name__ == "__main__":
    root = tk.Tk()
    game = ReactionGame(root)
    root.mainloop()
