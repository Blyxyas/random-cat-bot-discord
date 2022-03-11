CREATE TABLE IF NOT EXISTS servers (
	serverID INTEGER NOT NULL,
	user PRIMARY KEY(serverID)
);

-- Each server has a list of users
CREATE TABLE IF NOT EXISTS user (
	userid INTEGER NOT NULL PRIMARY KEY,
	cat_counter INTEGER NOT NULL DEFAULT 0,
	last_time INTEGER FOREIGN KEY (userid) REFERENCES servers(user)
);