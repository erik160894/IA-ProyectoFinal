
$(document).ready(() => {
    $.get('/tool/files', (res) => {
        if (!res.success) {
            return alert('Error.');
        }

        let listGroup = $('#list-group');
        res.data.forEach(file => {
            let date = new Date(file.timestamp);
            listGroup.append(`<a id="${file.file_name}" class="list-group-item list-group-item-action" name="fileListItem">${date}</a>`);
        });

        let currentActive = null;

        $('a[name=fileListItem]').on('click', (e) => {
            let fname = e.target.id;

            $('#audio-player').prop('src', '/data/' + fname);
            // $('#info-playe').innerText = e.target.innerText;

            if (currentActive) {
                currentActive.removeClass('active');
            }

            currentActive = $(e.target);
            currentActive.addClass('active');
        });
    });
});