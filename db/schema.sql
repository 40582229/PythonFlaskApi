DROP TABLE if EXISTS user;

CREATE TABLE user(
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    token TEXT
);

DROP TABLE if EXISTS excersises;

CREATE TABLE excersises(
    excersiseId INTEGER PRIMARY KEY AUTOINCREMENT,
    excersisename text NOT NULL,
    userid INTEGER NOT NULL,
    reps INTEGER,
    eSets INTEGER,
    crdate TEXT,
    FOREIGN KEY (userid) REFERENCES user(userid)
);