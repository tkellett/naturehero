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