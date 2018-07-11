const router = require('express').Router();

const datasetModel = require('../models/dataset-model');

router.get('/', (req, res, next) => {
    datasetModel.getAporte()
        .then(result => {
            res.render('progress', result);
        })
        .catch(next);
});

module.exports = router;