

// Signup function (example)
async function signup(email, password) {
  auth.createUserWithEmailAndPassword(email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      console.log("User created:", user);
    })
    .catch((error) => {
      console.error("Error:", error.message);
      alert("Error:", error.message);
    });
};

// Login function (example)
async function login(email, password) {
  auth.signInWithEmailAndPassword(email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      console.log("User signed in:", user);
    })
    .catch((error) => {
      console.error("Error:", error.message);
      alert("Error:", error.message);
    });
};

async function google_login() {
  const provider = new firebase.auth.GoogleAuthProvider();
  auth.signInWithPopup(provider)
    .then((result) => {
      const user = result.user;
      console.log("Google user:", user);
    })
    .catch((error) => {
      console.error("Error:", error.message);
    });
}

var onload = function () {
  document.getElementById('sign-out').onclick = function () {
    auth.signOut();
  };

  const googleButton = document.getElementById("google-sign-in-button");
  googleButton.addEventListener("click", () => {
    google_login();
  });

  // Example usage (in a button click handler, for instance)
  const signupButton = document.getElementById("signupButton");
  signupButton.addEventListener("click", () => {
    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;
    signup(email, password);
  });

  const loginButton = document.getElementById("loginButton");
  loginButton.addEventListener("click", () => {
    const email = document.getElementById("emailInput").value;
    const password = document.getElementById("passwordInput").value;
    login(email, password);
  });
  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
      // Comment out any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
      //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
      //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
      //firebase.auth.GithubAuthProvider.PROVIDER_ID,
      //firebase.auth.PhoneAuthProvider.PROVIDER_ID

    ],
    // Terms of service url.
    tosUrl: '<your-tos-url>'
  };

  auth.onAuthStateChanged(function (user) {
    if (user) {
      // User is signed in, so display the "sign out" button and login info.
      document.getElementById('signout-container').hidden = false;
      document.getElementById('login-info').hidden = false;
      document.getElementById('login-container').hidden = true;
      console.log(`Signed in as ${user.displayName} (${user.email})`);
      user.getIdToken().then(function (token) {
        // Add the token to the browser's cookies. The server will then be
        // able to verify the token against the API.
        // SECURITY NOTE: As cookies can easily be modified, only put the
        // token (which is verified server-side) in a cookie; do not add other
        // user information.
        document.cookie = "token=" + token;
      });
    } else {
      // User is signed out.
      // Initialize the FirebaseUI Widget using Firebase.
      // var ui = new firebaseui.auth.AuthUI(firebase.auth());
      // Show the Firebase login button.
      // ui.start('#firebaseui-auth-container', uiConfig);
      // Update the login state indicators.
      document.getElementById('signout-container').hidden = true;
      document.getElementById('login-info').hidden = true;
      document.getElementById('login-container').hidden = false;
      // Clear the token cookie.
      document.cookie = "token=";
    }
  }, function (error) {
    console.log(error);
    alert('Unable to log in: ' + error)
  });
}

window.addEventListener('load', onload);