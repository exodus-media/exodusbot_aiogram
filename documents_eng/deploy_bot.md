[Русский](../documents/deploy_bot.md)

# Deploy the bot at your server

To start the bot, you need to:
- clone the repository to the desired location (local computer or remote server);
- prepare a PostgreSQL database. Namely, install PostgreSQL on your server, create a user and password, create a database. Remember this data;
- create a config file.py in the data directory by analogy with the file config.test.py by filling in the current API_TOKEN and DATABASE_URL_PG;
- when using the bot locally on your home computer, set it in the file config.py DEBUG = True. If the bot is run on an industrial scale on the server, then specify DEBUG = False and at the same time fill in the values of WEBHOOK_, which are generated according to the instructions for WEBHOOK;
- install the necessary modules and packages for the bot using the command "pip install-r requirements.txt";
- install "sudo apt install systemd" (if it is not already installed);
- install redis-server using the command " sudo apt install redis-server";
- start / disable redis-server using the commands "sudo systemctl start redis-server" / " sudo systemctl enable redis-server";
- set the multi-language bot, being in the root of the project " pybabel compile-d locales -D testbot"
- launch app.py (it is advisable to add this script for execution via systemctl).

---
> [README_rus](../README.md)  |  [README_eng](../README_eng.md)  
> [Description of the bot for direct targeted assistance](documents_eng/index.md)

