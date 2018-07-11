$(document).ready(() => {
    let journalists = {
        j01: "Raúl Vargas",
        j02: "Patricia del Rio",
        j03: "Jose Maria Salcedo (Chema)",
        j04: "Aldo Mariátegui",
        j05: "Fernando Carvallo",
        j06: "Mónica Delta",
        j07: "Helmer Huerta",
        j08: "Guillermo Rossinni",
        j09: "Hector Felipe",
        j10: "Daniel Kanashiro",
        jxx: "Otro"
    };

    // Loading journalists
    let journalistsDiv = $('#dataSet-journalists');
    Object.keys(journalists).forEach(jKey => {
        journalistsDiv.append(`<div class="col-md-6"><div class="form-group form-check">
                        <input type="checkbox" class="form-check-input" id="j-cbx-${jKey}">
                        <label for="j-cbx-${jKey}" class="form-check-label">${journalists[jKey]}</label>
                    </div></div>`);
    });

    function getNext(current_id) {
        $.get('/api/next?id=' + current_id, res => {
           if (!res.success) {
               return alert('No more data samples');
           }

           let data = res.data;
           $('#dataSet-id').val(data.id);

           let timestamp = parseInt(data.id.substr(3))*1000;
           $('#dataSet-date').val(new Date(timestamp));
           $('#dataSet-tagger').val(data.tagger || '');
           $('#dataSet-audio').prop('src', '/audios/' + data.id + '.mp3');

           Object.keys(journalists).forEach(jKey => {
               $('#j-cbx-' + jKey).prop('checked', false);
           });

           if (data.tag) {
               data.tag.split(',').forEach(tag => {
                   $('#j-cbx-' + tag).prop('checked', true);
               });
           }
        });
    }

    $("#dataSet-get-first-button").on('click', () => {
        let val = $('#dataSet-start-date').val();
        if (val) {
            val = Date.parse(val).valueOf();
            val = Math.round(val/1000);
        } else {
            val = "00000000";
        }
        getNext('rpp' + val);
    });

    $("#btn-next-id").on('click', () => {
        let current_id = $('#dataSet-id').val() || 'rpp000000';
        getNext(current_id);
    });

    $('#btn-save-id').on('click', () => {
        let current_id = $('#dataSet-id').val();
        if (!current_id) {
            return alert('Nothing to save');
        }
        let tagger = $('#tagger-name-input').val();
        if (!tagger) {
            return alert('Tagger name is required');
        }

        let tags = Object.keys(journalists).filter(jKey => $('#j-cbx-' + jKey).prop('checked'));
        $.post('/api/save', {id: current_id, tag: tags.join(','), name: tagger}, (res) => {
            if (!res.success) {
                return alert('Error ☹');
            }
            alert('Saved ☺');
        });
    });

    $('#tagger-name-input').on('focusout', () => {
        let name = $('#tagger-name-input').val();
        localStorage.setItem('tagger-name', name);
    });

    $('#tagger-name-input').val(localStorage.getItem('tagger-name'));
});