const LIMIT_TASK_LEN = 1000;
const LIMIT_TASK_LIST_LEN = 100;

let task_uid_attr = 'data-js-task-uid';
let list_uid_attr = 'data-js-task-list-uid';

function focus(elem) {
    elem.focus();
    elem.select();
}


function createTaskEl(id, title) {
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


function loadTasks(list_uid) {
    fetch(new Request(`/list/${list_uid}/task`))
    .then(function(response) { return response.json(); })
    .then(function(response_json) {
        let container = document.querySelector(`#task_list_edit`);
        let tasks = response_json['tasks'];
        tasks.forEach(function(el, index, array) {
            li = createTaskEl(el.id, el.title);
            container.appendChild(li);
        });

        if (tasks.length < LIMIT_TASK_LIST_LEN) {
            for (var i=0; i <= LIMIT_TASK_LIST_LEN - tasks.length; i++) {
                li = createTaskEl(0, '');
                container.appendChild(li);
            }
        }

        focus(document.querySelector(`#task_list_edit input`));
    });
}


function handleChangeTaskTitle(e, list_uid) {
    // todo trotling
    let input = e.target
    let new_value = input.value;
    let current_li = input.closest(`li[${task_uid_attr}]`);
    let task_uid = current_li.getAttribute(task_uid_attr)

    // add task if value not empty
    if (!!new_value) {
        let form = new FormData()
        form.append('title', new_value);
        fetch(`/list/${list_uid}/task/${task_uid}`, {method: "PUT",  body: form})
        .then(function(response) { return response.json(); })
        .then(function(response_json) {
            current_li.setAttribute(task_uid_attr, encodeURIComponent(response_json['task_uid']))
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {

    let list_uid = document.querySelector(`#task_list_edit`).getAttribute(list_uid_attr);

    // init task list
    loadTasks(document.querySelector(`#task_list_edit`).getAttribute(list_uid_attr));


    // task title change handler
    document.addEventListener('keyup',  function(e) {
        if (e.target.matches(`li[${task_uid_attr}] input`)) {
            handleChangeTaskTitle(e, list_uid);
        }
    });
});
