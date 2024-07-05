### Hexlet tests and linter status:
[![Actions Status](https://github.com/dmkael/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/dmkael/python-project-83/actions)
[![linter](https://github.com/dmkael/python-project-83/actions/workflows/linter.yml/badge.svg)](https://github.com/dmkael/python-project-83/actions/workflows/linter.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/198b08924883bb5d1b22/maintainability)](https://codeclimate.com/github/dmkael/python-project-83/maintainability)

---

### Анализатор страниц
##### (Course project 3)
Данный веб-сервис позволяет произвести проверку веб-сайтов в интернете на базовую SEO-пригодность с помощью проверки наличия минимальной необходимой информации в ответах веб-страниц.\
Для проверки введите в поле на главной странице адрес интересующего ресурса, нажмите кнопку "Проверить" и запустите проверку. При успешном получении ответа результаты проверки отобразятся в таблице. Все результаты сохраняются в базу данных.

Проверить работу и протестировать можно по ссылке: [Page Analizer](https://python-project-83-2ssw.onrender.com).

\
Инструкция по установке и запуску сервиса у себя:

<details>
<summary>1. Системные требования</summary>

- Python 3.10 или выше ([скачать](https://www.python.org/downloads/))
- GIT-клиент ([скачать](https://git-scm.com/downloads/))
- Сервер с базой данных PostgreSQL ([скачать](https://www.postgresql.org/download/))

</details>

<details>
<summary>2. Порядок установки</summary>

- __Linux__:
  - для текущего пользователя:

      ```
    python3 -m pip install --user git+https://github.com/dmkael/python-project-83.git
      ```

  - в систему (использует встроенную версию Python):

      ```
    python3 -m pip install git+https://github.com/dmkael/python-project-83.git
      ```

- __Windows__:
  - для текущего пользователя:

      ```
    py -m pip install --user git+https://github.com/dmkael/python-project-83.git
      ```

  - в систему:

      ```
    py -m pip install git+https://github.com/dmkael/python-project-83.git
      ```

  _ВНИМАНИЕ: При установке пакета "для пользователя" необходимо, чтобы каталог пользовательских пакетов был доступен в переменной PATH. Детальная информация здесь:_
  _[Installing to the user documentation](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-to-the-user-site)_

Для работы сервиса необходимы две переменные окружения:

- SECRET_KEY - со значением секрета для работы приложения (можете любое значение сгенерировать сами)
- DATABASE_URL - путь к вашей подготовленной базе данных в виде унифицированного идентификатора ресурса (URI): _postgres://{user}:{password}@{hostname}:{port}/{database-name}_


  Можно использовать пакет python-dotenv и указать переменные в файле .env в корне пакета.
  Либо прописать переменные в окружение ОС:
- __Linux (Ubuntu):__

  - Вывести имеющиеся
    ```
    printenv
    ```
  - задать для пользователя, указав значение вида MY_VAR=VALUE:
    ```
    echo MY_VAR=VALUE >> $HOME/.bashrc
    ```
  - задать для системы, указав значение вида MY_VAR=VALUE:
    ```
    sudo echo MY_VAR=VALUE >> /etc/environment
    ```
    _Либо можете прописать текстовым редактором, например, nano в указанные файлы вручную._


- __Windows:__
  - запустить в командной строке __cmd__ или __PowerShell__ от имени администратора, либо в меню __Выполнить__, которое открывается сочетанием клавиш __WIN + R__ (_При запуске через меню "Выполнить" может запуститься без прав администратора, что не позволит менять системные переменные_):
    ```
    rundll32.exe sysdm.cpl,EditEnvironmentVariables
    ```

После добавления переменных окружения нужно подготовить базу данных:

- __Linux:__

  - запустить команду:
  ```
  python3 $(pip show hexlet-code | grep -oP 'Location: \K.*')/page_analyzer/load_db_schema.py
  ```

- __Windows:__
  
  - запустить команду в __PowerShell__:
  ```
  pip show hexlet-code | ForEach-Object {
      if ($_ -match 'WARNING: (.*)') {} else {
          $_ | Select-String -Pattern 'Location: (.*)' | ForEach-Object {
              if ($_.Matches.Count -gt 0) {
                  $location = $_.Matches[0].Groups[1].Value
                  $schema = $location + "\page_analyzer\load_db_schema.py"
                  Write-Output $schema
              }
          } | py "$schema"
      }
  }
  ```

На этом установка завершена!
</details>

<details>
<summary>3. Запуск веб-сервиса</summary>

После установки веб-сервис готов к запуску. Вы можете опционально добавить переменную окружения __PORT__ для указания порта веб-сервиса.
В случае отсутствия переменной, используется значение по умолчанию __8000__. Запустить можно следующими командами:

- __Linux:__

  запуск c использованием __Flask__ с отладкой:
  ```
  flask --debug --app page_analyzer:app  run --port 8000 --host localhost
  ```
  запуск c использованием __gunicorn__:
  ```
  export PORT=${PORT:-8000}; gunicorn -w 5 -b 0.0.0.0:$PORT page_analyzer:app
  ```

- __Windows:__

  запуск через __PowerShell__ c использованием __Flask__ с отладкой:
  ```
  flask --debug --app page_analyzer:app  run --port 8000 --host localhost
  ```
  ОС Windows не поддерживает __gunicorn__, поэтому в качестве альтернативы можете использовать __waitress__:
  ```
  pip install waitress
  ```
  запуск через __PowerShell__ c использованием __waitress__:
  ```
  if (-not $env:PORT) {$env:PORT = "8000"} waitress-serve --listen=*:$env:PORT page_analyzer:app
  ```

Остановить сервис можно сочетанием клавиш __CTRL + C__, либо закрытием окна терминала.
</details>

<details>
  <summary>4. Удаление</summary>
  
Для удаления сервиса введите в командной строке: 

- __Linux__:

    ```
  python3 -m pip uninstall hexlet-code
    ```

- __Windows__:

    ```
  py -m pip uninstall hexlet-code
    ```

</details>

Вы можете клонировать репозиторий себе и в дальнейшем развернуть его на хостинге. Имеющиеся команды в __Makefile__ могут быть вам полезны в использовании шаблона __database.sql__ для загрузки схемы в базу данных PostgreSQL, а так же в отладке и в сборке. 

Так же вы можете запустить сервис через контейнеры Docker.

<details>
<summary>Запуск через Docker</summary>

Системные требования для запуска через Docker:

- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop/))
    
1. Скачайте и поместите [docker-compose](blob:https://github.com/ca3cc8b6-ce65-43a7-b910-9aaabe0794fa) файл в любой пустой каталог.
   
   _Вы можете указать своё значение для порта в compose.yml если необходимо_
3. Создайте __.env__ внутри созданного каталога и укажите 4 переменных окружения в __.env__ файле с помощью любого текстового редактора:
   - __DB_USER__ - любое имя пользователя базы данных
   - __DB_PASSWORD__ - любой пароль для доступа к базе данных
   - __DB_NAME__ - любое имя базы данных
   - __SECRET_KEY__ - любое значение секретного ключа
4. Перейдите в каталог с помощью командной строки и выполните в нём команду:
   ```
   docker-compose -f compose.yml up
   ```

5. Сервис запустится и будет доступен по адресу [localhost:8000](http://localhost:8000/) (если значение порта не было отдредактировано в compose.yml). Чтобы остановить сервис нажмите сочетание клавиш __CTRL+C__ или остановите контейнеры через Docker Desktop или через коммандную строку с помощью docker.

</details>
