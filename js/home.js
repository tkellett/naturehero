document.addEventListener('DOMContentLoaded', () => {
    // Profile picture cycling
    const pictures = [
        'https://via.placeholder.com/200',
        'https://via.placeholder.com/200/ff0000',
        'https://via.placeholder.com/200/00ff00'
    ];
    
    let currentPictureIndex = 0;
    const profilePic = document.getElementById('profile-pic');
    
    profilePic.addEventListener('click', () => {
        currentPictureIndex = (currentPictureIndex + 1) % pictures.length;
        profilePic.src = pictures[currentPictureIndex];
    });

    // Task system
    const newTaskInput = document.getElementById('new-task');
    loadSavedTasks();

    window.addNewTask = () => {
        const taskText = newTaskInput.value.trim();
        const taskType = document.getElementById('task-type').value;
        console.log('Task Type:', taskType, 'Element:', document.getElementById('task-type'));
        
        if (taskText) {
            createTaskElement(taskText, taskType);
            newTaskInput.value = '';
            saveTasks();
            updateProgress();
        }
    };

    newTaskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addNewTask();
    });

    // Initialize progress
    updateProgress();
});

function createTaskElement(taskText, category, isChecked = false) {
    // Add error handling for category
    console.log('Creating task:', taskText, 'Category:', category);
    const validCategories = ['daily', 'weekly', 'monthly'];
    if (!validCategories.includes(category)) {
        console.error('Invalid category:', category);
        return;
    }

    const taskList = document.querySelector(`.task-list[data-category="${category}"]`);
    
    if (!taskList) {
        console.error('Task list not found for category:', category);
        return;
    }

    // Rest of the function remains the same
    const newTask = document.createElement('label');
    newTask.className = 'task-item';
    newTask.innerHTML = `
        <input type="checkbox" class="task" ${isChecked ? 'checked disabled' : ''}>
        <span>${taskText}</span>
    `;
    
    if (!isChecked) {
        newTask.querySelector('.task').addEventListener('change', function() {
            if (this.checked) {
                moveToDone(this.parentElement);
                updateProgress();
                saveTasks();
            }
        });
    }
    
    taskList.appendChild(newTask);
}

function moveToDone(taskElement) {
    const doneList = document.querySelector('.task-list[data-category="done"]');
    const clonedTask = taskElement.cloneNode(true);
    clonedTask.querySelector('input').disabled = true;
    doneList.appendChild(clonedTask);
    taskElement.remove();
}

function saveTasks() {
    const tasks = [];
    
    ['daily', 'weekly', 'monthly'].forEach(category => {
        const items = document.querySelectorAll(`.task-list[data-category="${category}"] .task-item`);
        items.forEach(item => {
            tasks.push({
                text: item.querySelector('span').textContent,
                category: category,
                checked: item.querySelector('input').checked
            });
        });
    });

    const doneTasks = document.querySelectorAll('.task-list[data-category="done"] .task-item');
    doneTasks.forEach(item => {
        tasks.push({
            text: item.querySelector('span').textContent,
            category: 'done',
            checked: true
        });
    });

    localStorage.setItem('tasks', JSON.stringify(tasks));
}

function loadSavedTasks() {
    const savedTasks = JSON.parse(localStorage.getItem('tasks')) || [];
    savedTasks.forEach(task => {
        if (task.category === 'done') {
            // Directly add to done list without using createTaskElement
            const doneList = document.querySelector('.task-list[data-category="done"]');
            const doneTask = document.createElement('label');
            doneTask.className = 'task-item';
            doneTask.innerHTML = `
                <input type="checkbox" class="task" checked disabled>
                <span>${task.text}</span>
            `;
            doneList.appendChild(doneTask);
        } else {
            createTaskElement(task.text, task.category, task.checked);
            if (task.checked) {
                moveToDone(document.querySelector(`.task-list[data-category="${task.category}"] .task-item:last-child`));
            }
        }
    });
}

function updateProgress() {
    const activeTasks = document.querySelectorAll('.task-list[data-category]:not([data-category="done"]) .task:checked');
    const totalXP = activeTasks.length * 5;
    const level = Math.floor(totalXP / 20) + 1;
    const progress = ((totalXP % 20) / 20) * 100;

    document.getElementById('progress').style.width = `${progress}%`;
    document.getElementById('level').textContent = level;
}