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

    // Initialize date inputs
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start-date').min = today;
    
    // Date input handlers
    document.getElementById('start-date').addEventListener('change', function() {
        document.getElementById('end-date').min = this.value;
        if (new Date(this.value) > new Date(document.getElementById('end-date').value)) {
            document.getElementById('end-date').value = '';
        }
    });

    document.getElementById('end-date').addEventListener('change', function() {
        if (new Date(this.value) < new Date(document.getElementById('start-date').value)) {
            this.value = '';
        }
    });

    // Task system initialization
    const newTaskInput = document.getElementById('new-task');
    loadSavedTasks();

    newTaskInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') addNewTask();
    });
});

// XP system constants
const XP_PER_TASK = 5;
const XP_PER_LEVEL = 20;
let currentLevel = 1;

// Global function for button click
function addNewTask() {
    const errorContainer = document.getElementById('error-message');
    errorContainer.style.display = 'none';
    
    const taskData = {
        text: document.getElementById('new-task').value.trim(),
        category: document.getElementById('task-type').value,
        startDate: document.getElementById('start-date').value,
        endDate: document.getElementById('end-date').value,
        tags: sanitizeTags(document.getElementById('task-tags').value)
    };

    // Validate inputs
    const errors = validateTaskData(taskData);
    
    if (errors.length > 0) {
        errorContainer.innerHTML = errors.join('<br>');
        errorContainer.style.display = 'block';
        window.scrollTo(0, 0);
        return;
    }

    // Proceed if valid
    createTaskElement(taskData);
    clearInputs();
    saveTasks();
    updateProgress();
}

function validateTaskData(taskData) {
    const errors = [];
    
    if (!taskData.text.trim()) errors.push('Task title is required');
    
    const today = new Date().setHours(0,0,0,0);
    const startDate = new Date(taskData.startDate).setHours(0,0,0,0);
    
    if (startDate < today) errors.push('Start date cannot be in the past');
    if (taskData.endDate && new Date(taskData.endDate) < new Date(taskData.startDate)) {
        errors.push('End date must be after start date');
    }
    
    if (taskData.tags.length > 5) errors.push('Maximum 5 tags allowed');
    if (taskData.tags.some(tag => tag.length > 15)) errors.push('Tags cannot be longer than 15 characters');
    
    return errors;
}

function sanitizeTags(tagString) {
    return tagString.split(',')
        .map(tag => tag.trim().replace(/[^a-zA-Z0-9 ]/g, ''))
        .filter(tag => tag.length > 0)
        .slice(0, 5);
}

function createTaskElement(taskData) {
    const taskList = document.querySelector(`.task-list[data-category="${taskData.category}"]`);
    
    const newTask = document.createElement('label');
    newTask.className = 'task-item';
    
    newTask.innerHTML = `
        <div class="task-header">
            <input type="checkbox" class="task">
            <span>${taskData.text}</span>
        </div>
        ${taskData.startDate ? `
        <div class="task-dates">
            <span>📅 Start: ${formatDate(taskData.startDate)}</span>
            ${taskData.endDate ? `<span> → End: ${formatDate(taskData.endDate)}</span>` : ''}
        </div>` : ''}
        ${taskData.tags.length > 0 ? `
        <div class="task-tags">
            ${taskData.tags.map(tag => `<span class="task-tag">#${tag}</span>`).join('')}
        </div>` : ''}
    `;

    newTask.querySelector('.task').addEventListener('change', function() {
        if (this.checked) {
            moveToDone(this.closest('.task-item'));
            saveTasks();
            updateProgress();
        }
    });

    taskList.appendChild(newTask);
}

function moveToDone(taskElement) {
    const doneList = document.querySelector('.task-list[data-category="done"]');
    const clonedTask = taskElement.cloneNode(true);
    
    clonedTask.querySelector('input').disabled = true;
    clonedTask.classList.add('xp-earned');
    doneList.appendChild(clonedTask);
    
    taskElement.remove();
}

function saveTasks() {
    const tasks = [];
    
    ['recurring', 'one-time', 'done'].forEach(category => {
        const items = document.querySelectorAll(`.task-list[data-category="${category}"] .task-item`);
        items.forEach(item => {
            tasks.push({
                text: item.querySelector('.task-header span').textContent,
                category: category,
                startDate: item.querySelector('.task-dates')?.textContent.match(/Start: (.*?) →/)?.[1],
                endDate: item.querySelector('.task-dates')?.textContent.match(/End: (.*)/)?.[1],
                tags: Array.from(item.querySelectorAll('.task-tag')).map(t => t.textContent.slice(1)),
                checked: item.querySelector('input').checked
            });
        });
    });

    localStorage.setItem('tasks', JSON.stringify(tasks));
}

function loadSavedTasks() {
    const savedTasks = JSON.parse(localStorage.getItem('tasks')) || [];
    savedTasks.forEach(task => {
        if (task.category === 'done') {
            const doneList = document.querySelector('.task-list[data-category="done"]');
            const doneTask = document.createElement('label');
            doneTask.className = 'task-item';
            doneTask.innerHTML = `
                <div class="task-header">
                    <input type="checkbox" class="task" checked disabled>
                    <span>${task.text}</span>
                </div>
                ${task.startDate ? `
                <div class="task-dates">
                    <span>📅 Start: ${task.startDate}</span>
                    ${task.endDate ? `<span> → End: ${task.endDate}</span>` : ''}
                </div>` : ''}
                ${task.tags.length > 0 ? `
                <div class="task-tags">
                    ${task.tags.map(tag => `<span class="task-tag">#${tag}</span>`).join('')}
                </div>` : ''}
            `;
            doneList.appendChild(doneTask);
        } else {
            createTaskElement(task);
        }
    });
    updateProgress();
}

function updateProgress() {
    const doneTasks = document.querySelectorAll('.task-list[data-category="done"] .task-item');
    const totalXP = doneTasks.length * XP_PER_TASK;
    const newLevel = Math.floor(totalXP / XP_PER_LEVEL) + 1;
    const progress = ((totalXP % XP_PER_LEVEL) / XP_PER_LEVEL) * 100;

    const levelElement = document.getElementById('level');
    
    // Animate level up
    if (newLevel > currentLevel) {
        levelElement.parentElement.classList.add('level-up');
        setTimeout(() => {
            levelElement.parentElement.classList.remove('level-up');
        }, 500);
        currentLevel = newLevel;
    }

    document.getElementById('progress').style.width = `${progress}%`;
    levelElement.textContent = newLevel;
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function clearInputs() {
    document.getElementById('new-task').value = '';
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    document.getElementById('task-tags').value = '';
}