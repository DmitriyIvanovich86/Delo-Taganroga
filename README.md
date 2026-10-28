# Дело Таганрога — иллюстрации

Карточки и иллюстрации к публикациям «Дело Таганрога» (MAX и Telegram).
Папка `cards/` — карточки-инфографики, имя файла: `ГГГГ-ММ-ДД_тема.png`.

## Публикация файлов для Telegram

`python3 tools/publish.py <файл> [--name имя]` — кладёт файл в ветку `files` и печатает публичную ссылку
`https://raw.githubusercontent.com/DmitriyIvanovich86/Delo-Taganroga/files/f/<имя>`, которую можно передать
в Telegram (sendPhoto / sendDocument по URL). Ветка `files` на Vercel не собирается (vercel.json).
Репозиторий публичный — персональные данные и договоры сюда не публикуются.
