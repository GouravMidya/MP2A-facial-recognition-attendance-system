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
setInterval(changeCategory, 4000);
