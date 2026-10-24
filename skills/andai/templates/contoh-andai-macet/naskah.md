---
slug: andai-macet
preset: standar
---

<!-- Contoh episode pilot. Angka belum diisi: semua fakta masih [[PERLU SUMBER]] di fakta.yaml. -->

## HOOK | dunia=andai | waktu=pagi
K01: Andai besok pagi kamu bangun, dan *macet* di kotamu hilang.

## ANDAI-1 | dunia=andai | waktu=pagi
K02: Kamu berangkat jam tujuh, dan jam tujuh lewat seperempat sudah sampai.
K03: Pedagang asongan di lampu merah sampai *bengong*, lampunya keburu hijau terus.

## PIVOT | dunia=andai
K04: Kedengarannya mustahil, ya? [jeda:0.5]

## NYATA-1 | dunia=nyata | waktu=pagi
K05: Padahal, di dunia nyata, pengendara di kota besar kita kehilangan {F1} di jalan setiap tahun.
K06: Kalau dikumpulkan, itu sama dengan {F1.konversi}.

## JEMBATAN-1 | dunia=andai
K07: Di duniamu yang baru, jam-jam itu pulang ke *meja makan*.

## ANDAI-2 | dunia=andai | waktu=siang
K08: Siangnya, ibumu ke pasar naik bus yang datang tepat waktu.
K09: Sopir angkot yang biasa ngetem malah *bingung* mau menunggu siapa.

## NYATA-2 | dunia=nyata | waktu=siang
K10: Di dunia nyata, baru {F2} perjalanan harian yang memakai transportasi umum.

## ANDAI-3 | dunia=andai | waktu=sore
K11: Sorenya, kamu pulang dan langit kota kelihatan *jernih*.

## NYATA-3 | dunia=nyata | waktu=sore
K12: Kembali ke dunia kita, macet bikin kerugian sampai {F3} setiap tahun.
K13: Kalau dibagi rata, itu {F3.konversi}.

## JEMBATAN-3 | dunia=andai
K14: Di sini, uang itu jadi *taman* dan trotoar.

## TWIST | dunia=netral | waktu=malam
K15: Malamnya, kamu mampir beli martabak.
K16: Refleks, kamu parkir di bahu jalan.
K17: Orang-orang di belakangmu nggak marah, mereka cuma *bingung*.
K18: Kotanya sudah berubah, kebiasaanmu belum. [jeda:0.6]

## REFLEKSI | dunia=netral | waktu=malam
K19: Di dunia nyata, {F4}.
K20: Macet bukan cuma soal jalan yang kurang lebar.
K21: Ada juga *lima menit* kecil yang kita ambil dari lajur orang lain.

## LOOP | dunia=andai | waktu=malam
K22: Kamu pindahkan motormu, antre sebentar, lalu pulang dan tidur.
K23: Karena kalau semua orang mulai dari parkir yang benar, mungkin… [jeda:0.8]
