-- Create table `users` with columns:
-- `user_id`: bigint unsigned not null primary key,
-- `username`: varchar(32) not null,
-- `discriminator`: varchar(4) not null,
-- `cat_counter`: int unsigned not null default 0,
-- `last_time`: timestamp not null,
-- Table `users` is used to store information about users.

CREATE TABLE IF NOT EXISTS users (
  guild_id bigint unsigned not null,
  userid bigint unsigned not null primary key,
  cat_counter int unsigned not null default 0,
  last_time timestamp not null
);

