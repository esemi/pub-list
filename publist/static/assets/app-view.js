"use strict";

const getTodoListApiEndpoint = './api/todolist/';

window.addEventListener('load', function () {
    console.log('app started');

    let todolistContainer = document.querySelector('.js-customer-todolist');

    init_app(todolistContainer);

}, false);


function init_app(container) {
    // todo checkbox onchange -> call lock_task_api
    // todo update task state after lock_task_api and show race-condition error (if actual)
}
