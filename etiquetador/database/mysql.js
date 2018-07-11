
const mysql = require('mysql');
const util = require('util');

const pool = mysql.createPool({
	host: process.env.MYSQL_HOST || '127.0.0.1',
	port: process.env.MYSQL_PORT || 3306,
	database: process.env.MYSQL_DB || 'ia',
	user: process.env.MYSQL_USER,
	password: process.env.MYSQL_PASSWORD
});

pool.queryAsync = util.promisify(pool.query);


module.exports = pool;