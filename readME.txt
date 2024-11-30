1) python.exe -m venv venv
2) для Windows                                               
	.\venv\Scripts\activate 

для Линьки погуглите как запускать venv (там две строчки не помню какие)

3) pip install -r requirements.txt

ДЛЯ ИЗБЕЖАНИЯ ВОЗМОЖНОЙ БЛОКИРОВКИ АККАУНТА НУЖНО ПОЛУЧИТЬ api_id & api_hash
 • Переходим на сайт my.telegram.org
 • Авторизуемся под любым своим аккаунтом
 • Нажимаем ' (https://my.telegram.org/apps)API development tools (https://my.telegram.org/apps)' (https://my.telegram.org/apps) и заполняем рандомными данными App title и Short name, жмём Create Application.
 • Сохраняем себе App api_id и App api_hash
 • В скрипте открываем файл \bot\config\config.py и указываем там сохраненные ранее api_id и api_hash

КАК ДОБАВИТЬ АККАУНТЫ?
 • Запускаем командой python main.py вводим '2' ( без кавычек ) и следуем инструкции ( вводим название для сессии, номер телефона, код из ТГ и пароль, если установлена 2фа )

КАК ИСПОЛЬЗОВАТЬ ПРОКСИ?
 • Откройте файл \bot\config\proxies.txt и запишите в него свои прокси в формате http://login:password@IP:port

КАК УКАЗАТЬ ШАБЛОН ТУРНИРА?
 • открываем в браузере нот пиксель, жмем инструменты разработчика -> сеть -> выбираем фильтр Fetch/XHR -> высматриваем в столбце name что то типо 7539867890.png?time=1732982998548
цифру до .png копируем и вставляем в файле tapper.py TEMPLATE_ID

Как запустить автофарм:
Аналогично запускаем python main.py файл и тыкаем 1.