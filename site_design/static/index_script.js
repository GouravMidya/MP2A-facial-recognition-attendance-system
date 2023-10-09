const loginContainer = document.querySelector(".login-container");
const signupContainer = document.querySelector(".signup-container");
const loginLink = document.getElementById("login-link");
const signupLink = document.getElementById("signup-link");
const categories = ["Business and Workplace", "Educational Institutions", "Events and Gatherings"];
const categoryElement = document.getElementById("changing");
let currentIndex = 0;

function changeCategory() {
    categoryElement.style.opacity = 0;
    setTimeout(() => {
        currentIndex = (currentIndex + 1) % categories.length;
        categoryElement.textContent = categories[currentIndex];
        categoryElement.style.opacity = 1;
    }, 1000); // Adjust the delay as needed (1 second in this example)
}

// Change the category every 4 seconds (adjust the timing as needed)
setInterval(changeCategory, 3000);

// Function to toggle between login and signup forms
function toggleSignupForm(e) {
    e.preventDefault();
    loginContainer.style.display = "none";
    signupContainer.style.display = "block";
}

function toggleLoginForm(e) {
    e.preventDefault();
    loginContainer.style.display = "block";
    signupContainer.style.display = "none";
}

// Add click event listeners to the "Sign Up" and "Login" links
signupLink.addEventListener("click", toggleSignupForm);
loginLink.addEventListener("click", toggleLoginForm);