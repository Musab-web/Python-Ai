import tkinter as tk
import random
import time
from threading import Thread
from collections import Counter

# === Kelas AIPlayer dengan Naive Bayes ===
class AIPlayer:
    def __init__(self):
        # Menyimpan histori hasil koin dan tebakan pemain
        self.history_results = []
        self.history_player_guesses = []

    def learn(self, hasil_koin, tebakan_player):
        # Menyimpan data setiap ronde untuk dipelajari AI
        self.history_results.append(hasil_koin)
        self.history_player_guesses.append(tebakan_player)

    def naive_bayes_prediction(self):
        # Jika belum ada data, tebak acak
        if not self.history_results:
            return random.choice(["Head", "Tail"])

        # Hitung jumlah kemunculan hasil dan tebakan
        total_data = len(self.history_results)
        hasil_counts = Counter(self.history_results)
        tebakan_counts = Counter(zip(self.history_player_guesses, self.history_results))

        # Probabilitas awal P(Head) dan P(Tail)
        prob_head = hasil_counts["Head"] / total_data
        prob_tail = hasil_counts["Tail"] / total_data

        # Dapatkan tebakan terakhir pemain
        last_guess = self.history_player_guesses[-1]

        # Hitung P(Guess | Result) untuk masing-masing hasil
        # Menggunakan Laplace smoothing agar tidak dibagi 0
        def conditional(tebakan, hasil):
            return (tebakan_counts[(tebakan, hasil)] + 1) / (hasil_counts[hasil] + 2)

        p_guess_given_head = conditional(last_guess, "Head")
        p_guess_given_tail = conditional(last_guess, "Tail")

        # Hitung P(Hasil | Tebakan) menggunakan Naive Bayes
        p_head_given_guess = p_guess_given_head * prob_head
        p_tail_given_guess = p_guess_given_tail * prob_tail

        # Prediksi hasil koin selanjutnya
        return "Head" if p_head_given_guess > p_tail_given_guess else "Tail"

    def plan(self):
        # Fungsi utama untuk menentukan prediksi AI
        return self.naive_bayes_prediction()

# === GUI Game ===
class CoinGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Lempar Koin - Naive Bayes AI")

        # Skor awal
        self.player_score = 0
        self.ai_score = 0

        # Buat objek AI
        self.ai = AIPlayer()

        # Bangun UI
        self.build_widgets()

    def build_widgets(self):
        # Label instruksi
        self.label_info = tk.Label(self.root, text="Tebak hasil lemparan koin:", font=("Arial", 14))
        self.label_info.pack(pady=10)

        # Tombol tebakan pemain
        self.btn_head = tk.Button(self.root, text="Head", font=("Arial", 12), width=10,
                                  command=lambda: self.play_round("Head"))
        self.btn_tail = tk.Button(self.root, text="Tail", font=("Arial", 12), width=10,
                                  command=lambda: self.play_round("Tail"))
        self.btn_head.pack(pady=5)
        self.btn_tail.pack(pady=5)

        # Label untuk animasi hasil lemparan
        self.koin_label = tk.Label(self.root, text="", font=("Courier", 32))
        self.koin_label.pack(pady=10)

        # Label hasil ronde
        self.label_result = tk.Label(self.root, text="", font=("Arial", 12))
        self.label_result.pack(pady=10)

        # Label skor
        self.label_score = tk.Label(self.root, text="Skor Kamu: 0 | AI: 0", font=("Arial", 12))
        self.label_score.pack(pady=10)

    def nilai_koin(self, hasil):
        # Menentukan nilai dari hasil lemparan
        return 2 if hasil == "Head" else 1

    def animasi_lemparan(self):
        # Menampilkan animasi sebelum hasil keluar
        for _ in range(10):
            self.koin_label.config(text=random.choice(["H", "T"]))
            time.sleep(0.1)

        # Hasil akhir
        hasil = random.choice(["Head", "Tail"])
        self.koin_label.config(text="H" if hasil == "Head" else "T")
        return hasil

    def play_round(self, tebakan_player):
        # Nonaktifkan tombol saat animasi berjalan
        self.btn_head.config(state=tk.DISABLED)
        self.btn_tail.config(state=tk.DISABLED)

        # Jalankan logika game di thread terpisah
        def game_logic():
            # AI membuat tebakan
            tebakan_ai = self.ai.plan()

            # Animasi dan hasil lemparan
            hasil_koin = self.animasi_lemparan()

            # AI belajar dari hasil dan tebakan pemain
            self.ai.learn(hasil_koin, tebakan_player)

            # Cek apakah tebakan benar
            benar_player = tebakan_player == hasil_koin
            benar_ai = tebakan_ai == hasil_koin

            # Tambah skor jika benar
            if benar_player:
                self.player_score += self.nilai_koin(hasil_koin)
            if benar_ai:
                self.ai_score += self.nilai_koin(hasil_koin)

            # Tampilkan hasil dan skor
            teks = (
                f"Tebakan Kamu: {tebakan_player} ({'Benar' if benar_player else 'Salah'})\n"
                f"Tebakan AI: {tebakan_ai} ({'Benar' if benar_ai else 'Salah'})"
            )
            self.label_result.config(text=teks)
            self.label_score.config(text=f"Skor Kamu: {self.player_score} | AI: {self.ai_score}")

            # Cek apakah game selesai
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
                # Aktifkan tombol lagi untuk ronde berikutnya
                self.btn_head.config(state=tk.NORMAL)
                self.btn_tail.config(state=tk.NORMAL)

        Thread(target=game_logic).start()

# === Jalankan aplikasi ===
if __name__ == "__main__":
    root = tk.Tk()
    app = CoinGameGUI(root)
    root.mainloop()
