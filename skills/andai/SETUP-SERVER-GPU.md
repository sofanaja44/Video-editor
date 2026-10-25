# Menyambungkan server GPU ke Claude (Remote Control)

> **Cara yang dipakai sekarang** bukan menjalankan Claude Code di server GPU, melainkan mengendalikan server GPU
> sewaan dari server utama lewat `bash andai/gpu/gpu.sh` (kunci SSH, kirim kode, jalankan, ambil hasil). Server GPU
> boleh mati atau diganti; semua aset tersimpan di server utama. Lihat [`PINDAH-SERVER.md`](PINDAH-SERVER.md).
> Panduan Remote Control di bawah tetap berlaku bila Anda memang ingin menjalankan Claude Code langsung di server GPU.

Sesi cloud Claude Code tidak bisa masuk ke server lewat SSH (jaringannya hanya meneruskan HTTPS). Jadi
caranya dibalik: Claude Code dijalankan **di server GPU**, lalu disambungkan ke aplikasi Claude lewat
Remote Control. Claude bekerja langsung di server dan memakai GPU-nya.

Syarat: akun Claude paket Pro, Max, Team, atau Enterprise (API key tidak bisa), dan server tetap menyala
selama dipakai.

## Spesifikasi server

| Komponen | Pilihan |
|---|---|
| GPU | **NVIDIA RTX 5090** (32 GB VRAM) |
| Driver | NVIDIA 570 ke atas, varian `open` (wajib untuk seri RTX 50) |
| OS | Ubuntu 22.04 atau 24.04 |
| RAM | Minimal 32 GB |
| Disk | SSD 100 GB atau lebih |
| CPU | 8 core atau lebih (caption, audio, encode) |
| Blender | 5.2.3 LTS, dipasang otomatis oleh `andai/gpu/setup_server.sh` |

## Langkah

1. **Masuk ke server** dari komputermu:
   ```bash
   ssh <user>@<alamat-server> -p <port>
   ```

2. **Pasang Claude Code:**
   ```bash
   curl -fsSL https://claude.ai/install.sh | bash
   exec bash
   claude --version
   ```

3. **Login:** jalankan `claude`, ketik `/login`, ikuti link yang muncul (boleh dibuka di HP/laptop),
   lalu `/exit`.

4. **Ambil repo:**
   ```bash
   git clone https://github.com/sofanaja44/Video-editor.git
   cd Video-editor
   ```
   Kalau repo private, git meminta login GitHub: pakai username dan *personal access token*.

5. **Jalankan Remote Control di dalam tmux** (supaya tetap hidup walau SSH ditutup):
   ```bash
   sudo apt install -y tmux
   tmux new -s andai
   claude remote-control --name "ANDAI GPU"
   ```
   Jawab `y` untuk *Trust* folder dan *Enable Remote Control*. Keluar dari tmux tanpa mematikan:
   **Ctrl+B** lalu **D**. Masuk lagi: `tmux attach -t andai`.

6. **Buka sesinya** di aplikasi Claude Code atau https://claude.ai/code, pilih **"ANDAI GPU"**.

7. **Pesan pertama** untuk sesi itu:
   > Baca `skills/andai/README.md`, `skills/andai/ROADMAP.md`, dan
   > `skills/andai/references/04-arsitektur-pipeline.md`. Jalankan `bash andai/gpu/setup_server.sh`
   > untuk menyiapkan server RTX 5090 ini dan mengukur kecepatan render Blender (EEVEE dan Cycles GPU).
   > Catat hasilnya di dokumen, commit dan push, lalu lanjutkan Fase 3 di ROADMAP: bangun karakter dan
   > set dengan Blender lewat kode.

   Kalau langkah 1 di skrip gagal karena driver belum ada, pasang dulu driver NVIDIA (versi 570 ke atas,
   varian `open`), reboot, lalu jalankan lagi skripnya.

## Keamanan

- Jangan simpan password server di repo atau di file mana pun yang di-commit.
- Lebih aman login SSH memakai kunci (`ssh-keygen` + `ssh-copy-id`) daripada password.

Panduan resmi Remote Control: https://code.claude.com/docs/en/remote-control
