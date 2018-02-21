const LIMIT_TASK_LEN = 1000;
const LIMIT_TASK_LIST_LEN = 100;

let task_uid_attr = 'data-js-task-uid';
let list_uid_attr = 'data-js-task-list-uid';

function focus(elem) {
    if (elem) {
        elem.focus();
        elem.select();
    }
}


function createTaskEditElem(id, title) {
    let li = document.createElement('li');
    li.setAttribute(task_uid_attr, encodeURIComponent(id));
    let input = document.createElement('input');
    input.setAttribute('type', 'text')
    input.setAttribute('maxlength', LIMIT_TASK_LEN)
    input.setAttribute('value', title)
    input.appendChild(document.createTextNode(title))
    li.appendChild(input);
    return li;
}

function createTaskReadElem(id, title, checked) {
    let li = document.createElement('li');
    li.setAttribute(task_uid_attr, encodeURIComponent(id));
    let checkbox = document.createElement('input');
    checkbox.setAttribute('id', id)
    checkbox.setAttribute('type', 'checkbox')
    if (checked > 0) {
        checkbox.checked = true;
    }
    let label = document.createElement('label')
    label.setAttribute('for', id)
    label.appendChild(document.createTextNode(title));
    li.appendChild(checkbox);
    li.appendChild(label);
    return li;
}


function loadTasks(list_uid, read_only=false) {
    fetch(new Request(`/list/${list_uid}/task`), {credentials: 'same-origin',})
    .then(function(response) { return response.json(); })
    .then(function(response_json) {
        let container = document.querySelector(`ul[${list_uid_attr}]`);
        let tasks = response_json['tasks'];
        tasks.forEach(function(el, index, array) {
            let li = null;
            if (!!read_only) {
                li = createTaskReadElem(el.id, el.title, el.checked);
            } else {
                li = createTaskEditElem(el.id, el.title);
            }
            if (!!li) {
                container.appendChild(li);
            }
        });

        if (tasks.length < LIMIT_TASK_LIST_LEN && !read_only) {
            for (var i=0; i <= LIMIT_TASK_LIST_LEN - tasks.length; i++) {
                li = createTaskEditElem(0, '');
                container.appendChild(li);
            }
        }

        focus(document.querySelector(`#task_list_edit input`));
    });
}


function handleChangeTaskTitle(e, list_uid) {
    // todo trottling
    let input = e.target
    let new_value = input.value;
    let current_li = input.closest(`li[${task_uid_attr}]`);
    let task_uid = current_li.getAttribute(task_uid_attr)

    // add task if value not empty
    if (!!new_value) {
        let form = new FormData()
        form.append('title', new_value);
        fetch(`/list/${list_uid}/task/${task_uid}/upsert`, {
            credentials: 'same-origin',
            method: "PUT",
            body: form
        })
        .then(function(response) { return response.json(); })
        .then(function(response_json) {
            current_li.setAttribute(task_uid_attr, encodeURIComponent(response_json['task_uid']))
        });
    }
}


function handleChangeTaskCheck(e, list_uid) {
    let input = e.target
    let new_value = input.checked;
    let current_li = input.closest(`li[${task_uid_attr}]`);
    let task_uid = current_li.getAttribute(task_uid_attr)

    console.log(input);
    console.log(new_value);
    console.log(current_li);

    let form = new FormData()
    form.append('state', new_value);
    return fetch(`/list/${list_uid}/task/${task_uid}/check`, {
        credentials: 'same-origin',
        method: "PUT",
        body: form
    })
    .then(function(response) {
        // todo reload all tasks if incomplete task
    });
}



document.addEventListener('DOMContentLoaded', function() {
    let list_uid_edit = document.querySelector(`#task_list_edit`);
    let list_uid_read = document.querySelector(`#task_list_read`);

    if (list_uid_edit) {
        // init task edit-list
        loadTasks(list_uid_edit.getAttribute(list_uid_attr));

        // task title change handler
        document.addEventListener('input',  function(e) {
            if (e.target.matches(`li[${task_uid_attr}] input`)) {
                handleChangeTaskTitle(e, list_uid_edit.getAttribute(list_uid_attr));
            }
        });
    }

    if (list_uid_read) {
        // init task read-list
        loadTasks(list_uid_read.getAttribute(list_uid_attr), true);

        // task title change handler
        document.addEventListener('change',  function(e) {
            if (e.target.matches(`li[${task_uid_attr}] input`)) {
                handleChangeTaskCheck(e, list_uid_read.getAttribute(list_uid_attr));
            }
        });
    }

});
