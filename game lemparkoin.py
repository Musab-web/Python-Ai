import tkinter as tk
import random
import time
from threading import Thread
from collections import Counter

# === Kelas AIPlayer dengan Naive Bayes ===
class AIPlayer:
    def __init__(self):
        # Inisialisasi history hasil koin dan tebakan pemain (data belajar AI)
        self.history_results = []
        self.history_player_guesses = []

    def learn(self, hasil_koin, tebakan_player):
        # Simpan hasil koin dan tebakan pemain setiap ronde untuk analisis AI
        self.history_results.append(hasil_koin)
        self.history_player_guesses.append(tebakan_player)

    def naive_bayes_prediction(self):
        # Jika belum ada data, AI tebak secara acak
        if not self.history_results:
            return random.choice(["Head", "Tail"])

        # Hitung total data yang sudah terkumpul
        total_data = len(self.history_results)
        # Hitung frekuensi hasil koin
        hasil_counts = Counter(self.history_results)
        # Hitung frekuensi pasangan (tebakan pemain, hasil koin)
        tebakan_counts = Counter(zip(self.history_player_guesses, self.history_results))

        # Probabilitas dasar untuk hasil Head dan Tail
        prob_head = hasil_counts["Head"] / total_data
        prob_tail = hasil_counts["Tail"] / total_data

        # Ambil tebakan terakhir pemain sebagai fitur untuk prediksi
        last_guess = self.history_player_guesses[-1]

        # Fungsi menghitung probabilitas kondisional P(tebakan | hasil) dengan Laplace smoothing
        def conditional(tebakan, hasil):
            return (tebakan_counts[(tebakan, hasil)] + 1) / (hasil_counts[hasil] + 2)

        # Hitung P(tebakan terakhir | Head) dan P(tebakan terakhir | Tail)
        p_guess_given_head = conditional(last_guess, "Head")
        p_guess_given_tail = conditional(last_guess, "Tail")

        # Hitung probabilitas posterior P(Head|tebakan) dan P(Tail|tebakan) (Naive Bayes)
        p_head_given_guess = p_guess_given_head * prob_head
        p_tail_given_guess = p_guess_given_tail * prob_tail

        # Prediksi hasil koin berikutnya berdasar probabilitas tertinggi
        return "Head" if p_head_given_guess > p_tail_given_guess else "Tail"

    def plan(self):
        # Fungsi utama untuk AI menentukan prediksi hasil koin
        return self.naive_bayes_prediction()

# === GUI Game ===
class CoinGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Lempar Koin - Naive Bayes AI")

        # Skor awal pemain dan AI
        self.player_score = 0
        self.ai_score = 0

        # Membuat objek AIPlayer
        self.ai = AIPlayer()

        # Membuat komponen GUI
        self.build_widgets()

    def build_widgets(self):
        # Label instruksi untuk pemain
        self.label_info = tk.Label(self.root, text="Tebak hasil lemparan koin:", font=("Arial", 14))
        self.label_info.pack(pady=10)

        # Tombol tebakan pemain: Head dan Tail
        self.btn_head = tk.Button(self.root, text="Head", font=("Arial", 12), width=10,
                                  command=lambda: self.play_round("Head"))
        self.btn_tail = tk.Button(self.root, text="Tail", font=("Arial", 12), width=10,
                                  command=lambda: self.play_round("Tail"))
        self.btn_head.pack(pady=5)
        self.btn_tail.pack(pady=5)

        # Label untuk menampilkan animasi hasil lemparan koin
        self.koin_label = tk.Label(self.root, text="", font=("Courier", 32))
        self.koin_label.pack(pady=10)

        # Label untuk menampilkan hasil ronde (benar/salah)
        self.label_result = tk.Label(self.root, text="", font=("Arial", 12))
        self.label_result.pack(pady=10)

        # Label skor terkini
        self.label_score = tk.Label(self.root, text="Skor Kamu: 0 | AI: 0", font=("Arial", 12))
        self.label_score.pack(pady=10)

        # Tombol "Coba Lagi" untuk reset skor tapi simpan data AI, awalnya disembunyikan
        self.btn_retry = tk.Button(self.root, text="Coba Lagi", font=("Arial", 12), width=10,
                                   command=self.reset_game)
        self.btn_retry.pack(pady=10)
        self.btn_retry.pack_forget()  # Sembunyikan tombol saat game belum selesai

    def nilai_koin(self, hasil):
        # Mengembalikan nilai skor koin:
        # Head bernilai 2, Tail bernilai 1
        return 2 if hasil == "Head" else 1

    def animasi_lemparan(self):
        # Menampilkan animasi berganti-ganti 'H' dan 'T' sebelum hasil keluar
        for _ in range(10):
            self.koin_label.config(text=random.choice(["H", "T"]))
            time.sleep(0.1)  # jeda supaya terlihat animasi

        # Pilih hasil akhir secara acak
        hasil = random.choice(["Head", "Tail"])
        self.koin_label.config(text="H" if hasil == "Head" else "T")
        return hasil

    def play_round(self, tebakan_player):
        # Nonaktifkan tombol Head dan Tail saat animasi dan perhitungan berlangsung
        self.btn_head.config(state=tk.DISABLED)
        self.btn_tail.config(state=tk.DISABLED)

        # Jalankan logika game di thread terpisah agar GUI tidak nge-hang
        def game_logic():
            # AI membuat prediksi berdasarkan Naive Bayes
            tebakan_ai = self.ai.plan()

            # Jalankan animasi lempar koin dan dapatkan hasil koin
            hasil_koin = self.animasi_lemparan()

            # AI belajar dari hasil lemparan dan tebakan pemain
            self.ai.learn(hasil_koin, tebakan_player)

            # Cek apakah tebakan pemain dan AI benar
            benar_player = tebakan_player == hasil_koin
            benar_ai = tebakan_ai == hasil_koin

            # Tambah skor jika tebakan benar
            if benar_player:
                self.player_score += self.nilai_koin(hasil_koin)
            if benar_ai:
                self.ai_score += self.nilai_koin(hasil_koin)

            # Update tampilan hasil tebakan dan skor
            teks = (
                f"Tebakan Kamu: {tebakan_player} ({'Benar' if benar_player else 'Salah'})\n"
                f"Tebakan AI: {tebakan_ai} ({'Benar' if benar_ai else 'Salah'})"
            )
            self.label_result.config(text=teks)
            self.label_score.config(text=f"Skor Kamu: {self.player_score} | AI: {self.ai_score}")

            # Cek kondisi kemenangan (skor minimal 5)
            if self.player_score >= 5 or self.ai_score >= 5:
                hasil = "Hasil seri!"
                if self.player_score > self.ai_score:
                    hasil = "Selamat, kamu menang!"
                elif self.ai_score > self.player_score:
                    hasil = "AI menang. Coba lagi!"

                # Tampilkan hasil akhir di label hasil
                self.label_result.config(text=self.label_result.cget("text") + f"\n\n{hasil}")

                # Nonaktifkan tombol tebakan karena game selesai
                self.btn_head.config(state=tk.DISABLED)
                self.btn_tail.config(state=tk.DISABLED)

                # Tampilkan tombol Coba Lagi agar pemain bisa main ulang tanpa reset AI
                self.btn_retry.pack()
            else:
                # Jika game belum selesai, aktifkan tombol untuk ronde berikutnya
                self.btn_head.config(state=tk.NORMAL)
                self.btn_tail.config(state=tk.NORMAL)

        Thread(target=game_logic).start()

    def reset_game(self):
        # Reset skor pemain dan AI, tapi data AI tetap tersimpan untuk pembelajaran lanjutan
        self.player_score = 0
        self.ai_score = 0
        self.label_score.config(text=f"Skor Kamu: {self.player_score} | AI: {self.ai_score}")
        self.label_result.config(text="")
        self.koin_label.config(text="")

        # Sembunyikan tombol Coba Lagi
        self.btn_retry.pack_forget()

        # Aktifkan kembali tombol tebakan Head dan Tail
        self.btn_head.config(state=tk.NORMAL)
        self.btn_tail.config(state=tk.NORMAL)


# === Jalankan aplikasi ===
if __name__ == "__main__":
    root = tk.Tk()
    app = CoinGameGUI(root)
    root.mainloop()
