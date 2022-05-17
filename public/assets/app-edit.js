"use strict";

const getTodoListApiEndpoint = './api/todolist/';

window.addEventListener('load', function () {
    console.log('app started');

    let todolistContainer = document.querySelector('.js-owner-todolist');

    init_app(todolistContainer);

}, false);


function init_app(container) {
    // todo keyup enter -> create next li
    // todo focus on last li -> create next li
    // todo keyup backspace and value = '' and li.idx >= 3 -> remove li
    // todo keyup any button and value != '' -> call update_task_api
}
