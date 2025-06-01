import tkinter as tk
import random
import time
from threading import Thread
from collections import defaultdict

class AIPlayer:
    def __init__(self):
        self.data = []  # penyimpanan sementara dalam RAM

    def learn(self, hasil_koin, tebakan_player):
        self.data.append((tebakan_player, hasil_koin))

    def naive_bayes_prediction(self):
        if not self.data:
            return random.choice(["Head", "Tail"])

        counts = defaultdict(lambda: {"Head": 0, "Tail": 0})
        total = {"Head": 0, "Tail": 0}

        # Hitung frekuensi
        for tebakan, hasil in self.data:
            counts[tebakan][hasil] += 1
            total[hasil] += 1

        # Hitung probabilitas posterior (dengan asumsi tebakan terakhir pemain)
        last_guess = self.data[-1][0] if self.data else random.choice(["Head", "Tail"])
        prob_head = (counts[last_guess]["Head"] + 1) / (total["Head"] + 2)  # Laplace smoothing
        prob_tail = (counts[last_guess]["Tail"] + 1) / (total["Tail"] + 2)

        return "Head" if prob_head > prob_tail else "Tail"

    def plan(self):
        strategi = [self.naive_bayes_prediction()] * 6
        strategi += [random.choice(["Head", "Tail"])] * 2
        return random.choice(strategi)

class CoinGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Lempar Koin ")

        self.player_score = 0
        self.ai_score = 0
        self.ai = AIPlayer()

        self.build_widgets()

    def build_widgets(self):
        self.label_info = tk.Label(self.root, text="Tebak hasil lemparan koin:", font=("Arial", 14))
        self.label_info.pack(pady=10)

        self.btn_head = tk.Button(self.root, text="Head", font=("Arial", 12), width=10, command=lambda: self.play_round("Head"))
        self.btn_tail = tk.Button(self.root, text="Tail", font=("Arial", 12), width=10, command=lambda: self.play_round("Tail"))
        self.btn_head.pack(pady=5)
        self.btn_tail.pack(pady=5)

        self.koin_label = tk.Label(self.root, text="", font=("Courier", 32))
        self.koin_label.pack(pady=10)

        self.label_result = tk.Label(self.root, text="", font=("Arial", 12))
        self.label_result.pack(pady=10)

        self.label_score = tk.Label(self.root, text="Skor Kamu: 0 | AI: 0", font=("Arial", 12))
        self.label_score.pack(pady=10)

    def nilai_koin(self, hasil):
        return 2 if hasil == "Head" else 1

    def animasi_lemparan(self):
        for _ in range(10):
            hasil_singkat = random.choice(["H", "T"])
            self.koin_label.config(text=hasil_singkat)
            time.sleep(0.1)

        hasil = random.choice(["Head", "Tail"])
        self.koin_label.config(text="H" if hasil == "Head" else "T")
        return hasil

    def play_round(self, tebakan_player):
        self.btn_head.config(state=tk.DISABLED)
        self.btn_tail.config(state=tk.DISABLED)

        def game_logic():
            tebakan_ai = self.ai.plan()
            hasil_koin = self.animasi_lemparan()

            self.ai.learn(hasil_koin, tebakan_player)

            benar_player = tebakan_player == hasil_koin
            benar_ai = tebakan_ai == hasil_koin

            if benar_player:
                self.player_score += self.nilai_koin(hasil_koin)
            if benar_ai:
                self.ai_score += self.nilai_koin(hasil_koin)

            teks = (
                f"Tebakan Kamu: {tebakan_player} ({'Benar' if benar_player else 'Salah'})\n"
                f"Tebakan AI: {tebakan_ai} ({'Benar' if benar_ai else 'Salah'})"
            )
            self.label_result.config(text=teks)
            self.label_score.config(text=f"Skor Kamu: {self.player_score} | AI: {self.ai_score}")

            if self.player_score >= 5 or self.ai_score >= 5:
                hasil = "Hasil seri!"
                if self.player_score > self.ai_score:
                    hasil = "Selamat, kamu menang!"
                elif self.ai_score > self.player_score:
                    hasil = "AI menang. Coba lagi!"

                self.label_result.config(text=self.label_result.cget("text") + f"\n\n{hasil}")
                self.btn_head.config(state=tk.DISABLED)
                self.btn_tail.config(state=tk.DISABLED)
            else:
                self.btn_head.config(state=tk.NORMAL)
                self.btn_tail.config(state=tk.NORMAL)

        Thread(target=game_logic).start()

# Jalankan aplikasi
if __name__ == "__main__":
    root = tk.Tk()
    app = CoinGameGUI(root)
    root.mainloop()
