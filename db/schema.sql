DROP TABLE if EXISTS user;

CREATE TABLE user(
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    token TEXT
);