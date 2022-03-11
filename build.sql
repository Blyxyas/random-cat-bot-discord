-- Create table `servers` with columns:
-- `guild_id`: bigint unsigned not null primary key,
-- `prefix`: varchar(5) not null default '!',
-- users: List of users that have access to the bot.

CREATE TABLE IF NOT EXISTS servers (
  guild_id bigint unsigned not null primary key,
  prefix varchar(5) not null default '!',
);

-- Create table `users` with columns:
-- `user_id`: bigint unsigned not null primary key,
-- `username`: varchar(32) not null,
-- `discriminator`: varchar(4) not null,
-- `cat_counter`: int unsigned not null default 0,
-- `last_time`: timestamp not null,
-- Table `users` is used to store information about users.

CREATE TABLE IF NOT EXISTS users (
  userid bigint unsigned not null primary key,
  cat_counter int unsigned not null default 0,
  last_time timestamp not null
);

