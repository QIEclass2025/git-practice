# -*- coding: utf-8 -*-
import tkinter as tk
import random
import time
import requests
from PIL import Image, ImageTk
import io

class ReactionGame:
    def __init__(self, master):
        self.master = master
        self.master.title("포켓몬 순발력 테스트")
        self.master.geometry("400x550")

        # --- 상태 변수 초기화 ---
        self.circle = None
        self.start_time = None
        self.is_green = False
        self.game_over = False
        self.is_standby = False  # 시작 대기 상태 플래그
        self.is_trial_finished = False # 새로운 상태 플래그
        
        self.trial_times = []
        self.max_trials = 5
        self.current_trial = 0
        self.tk_poke_image = None
        # ------------------------
        
        # 게임 프레임
        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack()

        self.canvas = tk.Canvas(self.game_frame, width=400, height=350, bg="#f0f0f0")
        self.canvas.pack()

        self.message_label = tk.Label(self.game_frame, text="", font=("Helvetica", 14), fg="black")
        self.message_label.pack(pady=10)

        # 결과 프레임
        self.result_frame = tk.Frame(self.master)
        
        self.pokemon_image_label = tk.Label(self.result_frame, bg="white")
        self.pokemon_image_label.pack(pady=10)
        
        self.result_label = tk.Label(self.result_frame, text="", font=("Helvetica", 16), justify=tk.CENTER)
        self.result_label.pack(pady=10)

        self.retry_button = tk.Button(self.result_frame, text="재도전 (5회)", command=self.reset_game)
        self.retry_button.pack(side=tk.LEFT, padx=20, pady=20)

        self.exit_button = tk.Button(self.result_frame, text="게임 종료", command=self.master.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=20, pady=20)

        self.reset_game()

    def reset_game(self):
        """게임을 초기 상태로 완전히 리셋합니다."""
        self.trial_times = []
        self.current_trial = 0
        self.game_over = False
        self.result_frame.pack_forget()
        self.game_frame.pack()
        self.start_standby()

    def start_standby(self):
        """다음 시행을 위한 대기 상태로 진입합니다."""
        self.is_standby = True
        self.is_green = False
        self.start_time = None 
        self.game_over = False
        self.is_trial_finished = False 
        
        self.canvas.delete("all")
        # 대기 상태: 파란색 원으로 표시
        self.circle = self.canvas.create_oval(150, 100, 250, 200, fill="blue") 
        self.canvas.tag_bind(self.circle, "<Button-1>", self.on_circle_click)
        
        self.message_label.config(text=f"[{self.current_trial+1}/{self.max_trials}회] 원을 클릭하여 테스트를 시작하세요!", fg="black")
        
    def start_round(self):
        """딜레이를 설정하고 색상 변경을 예약합니다."""
        self.is_standby = False
        self.message_label.config(text="대기... 초록색이 되면 클릭하세요!", fg="red")
        self.canvas.itemconfig(self.circle, fill="red")
        
        self.schedule_color_change()

    def schedule_color_change(self):
        """2초에서 7초 사이의 무작위 딜레이 후 색상을 초록색으로 변경합니다."""
        delay = random.randint(2000, 7000)
        self.master.after(delay, self.change_color_to_green)

    def change_color_to_green(self):
        """원의 색상을 초록색으로 바꾸고 반응 시간 측정을 시작합니다."""
        if self.game_over or self.is_standby:
            return
        self.canvas.itemconfig(self.circle, fill="green")
        self.is_green = True
        self.start_time = time.time()

    def on_circle_click(self, event):
        """원 클릭 시 처리 로직입니다."""
        if self.game_over:
            return

        if self.is_standby:
            # 대기 상태 클릭 -> 테스트 시작
            self.start_round()
            return
        
        # 이미 결과를 처리 중이면 무시합니다.
        if self.is_trial_finished:
            return
        
        # --- 반응 테스트 로직 ---
        
        # 결과를 처리하기 시작했으므로 플래그를 True로 설정합니다.
        self.is_trial_finished = True 

        reaction_time = -1
        if self.is_green:
            # 성공적으로 초록색일 때 클릭
            reaction_time = (time.time() - self.start_time) * 1000  # ms
        else:
            # 초록색이 되기 전에 클릭 (Too Early)
            pass

        self.process_trial(reaction_time)

    def process_trial(self, reaction_time):
        """현재 시행 결과를 처리하고 다음 단계로 넘어갑니다."""
        
        self.current_trial += 1
        
        if reaction_time < 0:
            # 너무 빨리 클릭 (Too Early)
            self.show_trial_feedback("너무 빨리 클릭했습니다! (실패)", "red")
        elif reaction_time >= 0:
            # 성공적으로 클릭
            self.trial_times.append(reaction_time)
            self.show_trial_feedback(f"반응 시간: {reaction_time:.2f} ms", "blue")
            
        
        # 다음 단계로 이동 예약
        if self.current_trial >= self.max_trials:
            self.master.after(1500, self.show_final_results) # 1.5초 후 최종 결과 표시
        else:
            self.master.after(1500, self.start_standby) # 1.5초 후 다음 대기 상태

    def show_trial_feedback(self, message, color):
        """각 시행 후 간단한 피드백을 보여주고 원을 삭제합니다."""
        self.message_label.config(text=message, fg=color)
        
        # <--- 수정 사항: 캔버스에서 원을 아예 삭제합니다.
        if self.circle:
            self.canvas.delete(self.circle)
            self.circle = None
        # -----------------------------------------------

    def fetch_pokemon_data(self):
        """PokéAPI에서 무작위 포켓몬의 이름과 이미지 URL을 가져옵니다."""
        pokemon_id = random.randint(1, 151)
        pokeapi_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
        
        try:
            response = requests.get(pokeapi_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # 포켓몬 이름 (영문, 첫 글자 대문자)
            name = data['name'].capitalize()

            # 공식 아트워크 이미지 URL
            image_url = data['sprites']['other']['official-artwork']['front_default']
            
            return name, image_url
            
        except Exception as e:
            # 오류 발생 시 피카츄를 기본값으로 사용
            print(f"Error fetching Pokemon: {e}")
            return "Pikachu", "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"

    def display_pokemon_image(self, url):
        """주어진 URL의 포켓몬 이미지를 다운로드하여 결과 창에 표시합니다."""
        try:
            image_response = requests.get(url, timeout=5)
            image_response.raise_for_status()
            image_data = image_response.content
            
            pil_image = Image.open(io.BytesIO(image_data))
            pil_image.thumbnail((150, 150))
            self.tk_poke_image = ImageTk.PhotoImage(pil_image)
            
            self.pokemon_image_label.config(image=self.tk_poke_image)
            self.pokemon_image_label.image = self.tk_poke_image 

        except Exception as e:
            self.pokemon_image_label.config(text="이미지 로드 실패")
            print(f"Error displaying Pokemon image: {e}")

    def get_rank_text(self, time):
        """평균 시간에 따른 순위 텍스트를 반환합니다."""
        if time == 0:
            return "측정된 성공 기록이 없습니다."
        elif 0 < time <= 100:
            return "신! (최고 수준)"
        elif time <= 200:
            return "프로게이머! (매우 빠름)"
        elif time <= 300:
            return "고수! (상위권)"
        elif time <= 400:
            return "평균!"
        else:
            return "조금 더 노력하세요! (평균 이하)"

    def show_final_results(self):
        """최종 결과를 계산하고 Pokémon API 결과를 함께 보여줍니다."""
        self.game_over = True
        self.game_frame.pack_forget()
        self.result_frame.pack()
        
        # --- 1. 평균 반응 속도 계산 ---
        avg_time = sum(self.trial_times) / len(self.trial_times) if self.trial_times else 0
        
        # --- 2. Pokémon 데이터 가져오기 ---
        pokemon_name, pokemon_image_url = self.fetch_pokemon_data()
        
        # --- 3. 이미지 및 랭킹 표시 ---
        self.display_pokemon_image(pokemon_image_url)

        rank_text = self.get_rank_text(avg_time)
        
        final_message = (
            f"--- 최종 결과 ({len(self.trial_times)}/{self.max_trials}회 성공) ---\n"
            f"평균 반응 속도: {avg_time:.2f} ms\n\n"
            f"랭킹: {rank_text}"
        )

        pokemon_message = f"당신의 반응속도로는 포켓몬 **{pokemon_name}**이(가) 어울려요!!"
        
        self.result_label.config(text=final_message + "\n\n" + pokemon_message)


if __name__ == "__main__":
    # Pillow (PIL)과 requests가 설치되어 있어야 합니다.
    # pip install requests pillow
    root = tk.Tk()
    game = ReactionGame(root)
    root.mainloop()
