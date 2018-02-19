document.addEventListener('DOMContentLoaded', function() {
    const LIMIT_TASK_LEN = 1000;

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

            focus(document.querySelector(`#task_list_edit input`));
        });
    }

    function handleChangeTaskTitle(input) {
        // todo tortling
        let new_value = input.value;
        let current_li = input.closest(`li[${task_uid_attr}]`);
        let prev_li = current_li.previousSibling;
        let next_li = current_li.nextSibling;
        console.log(current_li);
        console.log(prev_li);
        console.log(next_li);
        console.log(new_value);

        // todo remove elem if empty
        // todo add next elem if key enter
        // todo save new value

    }


    // init task list
    loadTasks(document.querySelector(`#task_list_edit`).getAttribute(list_uid_attr));

    // task title change handler
    document.addEventListener('keyup', function(e) {
       if (e.target.matches(`li[${task_uid_attr}] input`)) {
           handleChangeTaskTitle(e.target);
       }
    });
});
