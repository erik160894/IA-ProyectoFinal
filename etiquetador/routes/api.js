const express = require('express');
const router = express.Router();

const datasetModel = require('../models/dataset-model');

router.post('/save', (req, res, next) => {
    let {id, tag, name} = req.body;

    if (!id || !tag || !name) {
        return res.json({
            success: false,
            message: 'Datos incompletos.'
        });
    }

    datasetModel.saveTag(id, tag, name)
        .then((result) => {
            res.json(result);
        }).catch(next);
});

router.get('/next', (req, res, next) => {
    let id = req.query.id;

    datasetModel.next(id)
        .then(dt => {
            res.json(dt);
        })
        .catch(next);
});

router.get('/:id', (req, res, next) => {
    let id = req.params.id;

    datasetModel.get(id)
        .then(dt => {
            res.json(dt);
        })
        .catch(next);
});

module.exports = router;
