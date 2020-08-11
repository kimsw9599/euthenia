create role role_user with login password 'password';
create database databasename with encoding='UTF8' owner=role_user;
grant all privileges on database databasename to role_user;
