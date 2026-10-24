# Menyambungkan server GPU ke Claude (Remote Control)

Sesi cloud Claude Code tidak bisa masuk ke server lewat SSH (jaringannya hanya meneruskan HTTPS). Jadi
caranya dibalik: Claude Code dijalankan **di server GPU**, lalu disambungkan ke aplikasi Claude lewat
Remote Control. Claude bekerja langsung di server dan memakai GPU-nya.

Syarat: akun Claude paket Pro, Max, Team, atau Enterprise (API key tidak bisa), dan server tetap menyala
selama dipakai.

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
   > Baca `skills/andai/ROADMAP.md` dan `skills/andai/references/04-arsitektur-pipeline.md` bagian 2.1.
   > Uji render 3D pakai GPU server ini: cek `nvidia-smi`, lalu jalankan
   > `andai/scene3d/prototipe/blender_scene.py` (EEVEE dan Cycles GPU) dan `render.js` (three.js).
   > Bandingkan waktu per frame dan hasil gambarnya, perbarui dokumen, lalu commit dan push.

## Keamanan

- Jangan simpan password server di repo atau di file mana pun yang di-commit.
- Lebih aman login SSH memakai kunci (`ssh-keygen` + `ssh-copy-id`) daripada password.

Panduan resmi Remote Control: https://code.claude.com/docs/en/remote-control
