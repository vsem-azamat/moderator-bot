
CREATE TABLE IF NOT EXISTS total_admins(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg       INTEGER UNIQUE,
    state       BOOLEAN DEFAULT 1
);
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS  users(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg       INTEGER UNIQUE,
    verify      BOOLEAN DEFAULT 1,
    q_respect   INTEGER DEFAULT 0,
    q_warn      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS black_list(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user     INTEGER ,

    FOREIGN KEY(id_user) REFERENCES users(id)
);

----------------------------------------------------------

--local admins in chats and they global states
CREATE TABLE IF NOT EXISTS admins(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg       INTEGER UNIQUE NOT NULL,
    state       BOOLEAN DEFAULT 1   --global states
);

--list of chats
CREATE TABLE IF NOT EXISTS chats(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg_chats INTEGER UNIQUE NOT NULL 
);

CREATE TABLE IF NOT EXISTS chat_admins(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_chat     INTEGER UNIQUE,
    id_admin    INTEGER,
    state       BOOLEAN DEFAULT 1, --local state in one chat

    FOREIGN KEY(id_admin)   REFERENCES admins(id),
    FOREIGN KEY(id_chat)    REFERENCES chats(id_tg_chats)
);

--welcome messages and "bot-test"
CREATE TABLE IF NOT EXISTS welcome_test(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_chat     INTEGER NOT NULL,
    text        TEXT,
    time_autodelete INTEGER DEFAULT 60,     --time for autodelete welcome messages on "seconds"
    state_text  BOOLEAN DEFAULT 0,          --row for on/off welcome test
    state_test  BOOLEAN DEFAULT 0,

    FOREIGN KEY(id_chat) REFERENCES chats(id)
);


--list of bot commands
CREATE TABLE IF NOT EXISTS commands(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    command     TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS command_states(
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_command  INTEGER NOT NULL,
    id_chat     INTEGER NOT NULL,
    state       BOOLEAN DEFAULT 1,
    
    FOREIGN KEY(id_command)    REFERENCES commands(id),
    FOREIGN KEY(id_chat)       REFERENCES chats(id)
);