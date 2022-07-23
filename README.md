# Бот модератор в Телеграмме.
Создан для модерирования моих образовательных чатов по Чехии в телеграмме. 

### Ссылки для ознакомления с ботом
- Бот: @konnekt_moder_bot
- Один из чатов с ботом: @cvut_chat

## Установка
1) `git clone *link*`
2) Создайте файл `.env` в главной директории бота, вписав туда `TOKEN=*BOT_TOKEN*`  

## Команды для модерирования

| Команда                 | Описание                                                                                                                                                                             |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MAIN                    |                                                                                                                                                                                      |
| `/mute *int* *m,h,d,w*` | Мутит пользователя в чате на указанное время первым параметром, по умолчанию: 5 минут. Вторым параметром задаются еденицы времени (минуты, часы, дни, недели), по умолчанию: минуты. |
| `/unmute`               | Снимает мут с пользователя в чате.                                                                                                                                                   |
| `/ban`                  | Банит пользователя с чата и добавляет в черный список                                                                                                                                |
| `/unban`                | Убирает пользователя с черного списка                                                                                                                                                |
| `/fullban`              | Бан пользователя со всех чатов и добавление в черный список.                                                                                                                         |
| WELCOME                 |                                                                                                                                                                                      |
| `/welcome`              | Включает приветственное сообщение в чате для новых участников чата.                                                                                                                  |
| `/welcome -s`           | Показывает текущие настройки приветствия для чата.                                                                                                                                   |
| `/welcome -b`           | Включает простую кнопку для проверки на бота в приветственном сообщении. Если пользователь уже когда-то прошел тест, повторно проходить не требуется.                                |
| `/welcome -d`           | Включает кнопки для проверки на бота в приветственном сообщении, где нужно выбрать актуальную дату. Если пользователь уже когда-то прошел тест, повторно проходить не требуется.     |
| `/welcome *text* `      | Меняет текст приветственного сообщения.                                                                                                                                              |
| `/welcome -t *int*`     | Меняет время автоудаления приветственного сообщения. Допустимый интервал: 10-900 секунд.                                                                                             |
| OTHER                   |                                                                                                                                                                                      |
| `/chats`                | Посылает список образовательных чатов из таблицы `ChatLinks` в `/db/moder_bot.db`                                                                                                    |
| `/gay`                  | Радугометр                                                                                                                                                                           |