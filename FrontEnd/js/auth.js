function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if(username && password) {
        localStorage.setItem('loggedInUser', username);
        window.location.href = 'home.html';
    } else {
        alert('Please enter credentials');
    }
}

function handleRegister() {
    const username = document.getElementById('reg-username').value;
    const fullName = document.getElementById('reg-name').value;
    const dob = document.getElementById('reg-dob').value;
    const password = document.getElementById('reg-password').value;

    if(username && fullName && dob && password) {
        // Store user data (you might want to use more secure storage in production)
        const userData = {
            username,
            fullName,
            dob,
            password
        };
        localStorage.setItem(username, JSON.stringify(userData));
        alert('Registration successful!');
        window.location.href = 'index.html';
    } else {
        alert('Please fill all fields');
    }
}