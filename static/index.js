document.addEventListener('DOMContentLoaded', function() {

    let bookmark_id_attr = 'data-js-bookmark';
    let torrent_id_attr = 'data-js-torrent';
    let favorites_offset = 0;
    let unsort_limit = 15;

    fetch(new Request('/stat.json'))
    .then(function(response) { return response.json(); })
    .then(function(response_json) {
        stat = response_json['stat']
        document.querySelector('#stat_last_update').innerHTML = new Date(stat['last_update'] * 1000).toISOString()
        document.querySelector('#stat_total_bookmarks').innerHTML = stat['total_bookmarks']
        document.querySelector('#stat_total_torrents').innerHTML = stat['total_torrents']
        document.querySelector('#stat_last_bookmark').innerHTML = stat['last_bookmark']
        document.querySelector('#stat_last_torrent').innerHTML = stat['last_torrent']
    });

    function loadBookmarks(type, limit) {
        fetch(new Request(`/bookmarks/${type}.json?limit=${limit}`))
        .then(function(response) { return response.json(); })
        .then(function(response_json) {
            let container = document.querySelector(`#${type} ul`);
            let bookmarks = response_json['bookmarks'];
            bookmarks.forEach(function(el, index, array) {
                let li = document.createElement('li');
                li.setAttribute(bookmark_id_attr, encodeURIComponent(el._id));
                li.appendChild(document.createTextNode(el._id));
                container.appendChild(li)
            });
        });
    }

    function loadTorrents(id) {
        fetch(new Request(`/torrents/${id}`))
        .then(function(response) { return response.json(); })
        .then(function(response_json) {
            let container = document.querySelector('#search_results');
            // clear old content
            container.innerHTML = "";

            let torrents = response_json['torrents'];
            if (!torrents.length) {
                let th = document.createElement('th');
                th.appendChild(document.createTextNode('Данных нет =('));
                container.appendChild(th)
            } else {
                torrents.forEach(function(el, index, array) {
                    let tr = document.createElement('tr');
                    tr.setAttribute(torrent_id_attr, encodeURIComponent(el._id));

                    let loadTd = document.createElement('td');
                    let loadHref = document.createElement('a')
                    loadHref.setAttribute('href', encodeURI(el.tor_link))
                    let loadIcon = document.createElement('div')
                    loadIcon.classList.add("download-icon");
                    loadHref.appendChild(loadIcon);
                    loadTd.appendChild(loadHref);
                    tr.appendChild(loadTd);

                    let sizeTd = document.createElement('td');
                    sizeTd.appendChild(document.createTextNode(`${el.size_gb.toFixed(2)} GB`))
                    tr.appendChild(sizeTd);

                    let titleTd = document.createElement('td');
                    let titleHref = document.createElement('a')
                    titleHref.setAttribute('href', encodeURI(el.link))
                    titleHref.setAttribute('target', '_blank')
                    titleHref.appendChild(document.createTextNode(el.title))
                    titleTd.appendChild(titleHref);
                    tr.appendChild(titleTd);

                    container.appendChild(tr)
                });
            }
        });
    }


    // load bookmark tabs
    loadBookmarks('unsort', unsort_limit);

    // load and show torrents for bookmark
    document.addEventListener('click', function(e) {
       if (e.target.matches(`li[${bookmark_id_attr}]`)) {
           loadTorrents(e.target.getAttribute(bookmark_id_attr));
       }
    }, false);

});
