const dbConn = require('../database/mysql');

const TABLE = 'dataset';


async function getStats() {
    let query = `select count(*) as total, sum(tag is not null) as advance from ${TABLE}`;
    let ans = await dbConn.queryAsync(query);
    return ans[0];
}

async function saveTag(id, tag, tagger) {
    let query = `update ${TABLE} set tag = ?, tagger = ? where id = ?`;
    let res = await dbConn.queryAsync(query, [tag, tagger, id]);

    return {success: res.affectedRows > 0};
}

async function getAporte() {
    let stats = await getStats();
    let query = `select tagger, count(*) as cnt from ${TABLE} where tagger is not null group by tagger`;
    let aporte = await dbConn.queryAsync(query);
    let query2 = `select tag, count(*) as cnt from ${TABLE} where tagger is not null group by tag`;
    let tag_count = await dbConn.queryAsync(query2);

    return {
        stats: stats,
        aport: aporte,
        tag_count: tag_count
    };
}

async function get(id) {
    let query = `select * from ${TABLE} where id = ?`;
    let row = await dbConn.queryAsync(query, [id]);

    if (row.length === 0) {
        return {success: false};
    }

    return {
        success: true,
        data: row[0]
    };
}

async function next(id) {
    let query = `select * from ${TABLE} where id > ? limit 1`;
    let row = await dbConn.queryAsync(query, [id]);

    if (row.length === 0) {
        return {success: false};
    }

    return {
        success: true,
        data: row[0]
    };
}

async function all() {
    let data = await dbConn.queryAsync('select id, tag, tagger from ' + TABLE);

    return {
        success: true,
        data: data
    };
}

module.exports = {
    saveTag: saveTag,
    getAporte: getAporte,
    get: get,
    next: next,
    all: all
};