// Dashboard script

// All navbar links
const viewattendanceLink = document.getElementById("viewattendanceLink");
const takeattendanceLink = document.getElementById("takeattendanceLink");
const addStudentLink = document.getElementById("addStudentLink");
const viewStudentLink = document.getElementById("viewStudentLink");
const nextdivlink = document.getElementById("nextdivlink");
const backdivlink = document.getElementById("backdivlink");
const nextButton = document.getElementById("nextButton");
// All containers
const viewattendancecontainer = document.getElementById("viewattendance-container");
const takeattendancecontainer = document.getElementById("takeattendance-container");
const addStudentContent = document.getElementById("addStudentContent");
const viewstudentcontainer = document.getElementById("viewstudent-container");
const addStudentContentP1 = document.getElementById("addStudentContentP1");
const addStudentContentP2 = document.getElementById("addStudentContentP2");

// Function to hide all content containers
function hideAllContainers() {
    viewattendancecontainer.style.display = "none";
    takeattendancecontainer.style.display = "none";
    addStudentContent.style.display = "none";
    viewstudentcontainer.style.display = "none";
}

// Initial setup: hide all containers
hideAllContainers();

// Event listeners for navigation links
viewattendanceLink.addEventListener("click", function () {
    // Select all elements with the class "myClass"
    var elements = document.querySelectorAll(".active");

    // Loop through the selected elements and remove the class
    elements.forEach(function(element) {
        element.classList.remove("active");
    });

    // Get the element by its ID
    var element = document.getElementById("viewattendanceLink");

    // Set the class for the element
    element.className = "active";


    hideAllContainers();
    viewattendancecontainer.style.display = "block";
});

takeattendanceLink.addEventListener("click", function () {
    // Select all elements with the class "myClass"
    var elements = document.querySelectorAll(".active");

    // Loop through the selected elements and remove the class
    elements.forEach(function(element) {
        element.classList.remove("active");
    });

    // Get the element by its ID
    var element = document.getElementById("takeattendanceLink");

    // Set the class for the element
    element.className = "active";


    hideAllContainers();
    takeattendancecontainer.style.display = "block";
});

addStudentLink.addEventListener("click", function () {
    // Select all elements with the class "myClass"
    var elements = document.querySelectorAll(".active");

    // Loop through the selected elements and remove the class
    elements.forEach(function(element) {
        element.classList.remove("active");
    });

    // Get the element by its ID
    var element = document.getElementById("addStudentLink");

    // Set the class for the element
    element.className = "active";


    hideAllContainers();
    addStudentContent.style.display = "block";
});


// Next Button to add Student
nextButton.addEventListener("click", function () {
    addStudentContentP1.style.display = "none";
    addStudentContentP2.style.display = "block";
});


viewStudentLink.addEventListener("click", function () {
    // Select all elements with the class "myClass"
    var elements = document.querySelectorAll(".active");

    // Loop through the selected elements and remove the class
    elements.forEach(function(element) {
        element.classList.remove("active");
    });

    // Get the element by its ID
    var element = document.getElementById("viewStudentLink");

    // Set the class for the element
    element.className = "active";

    hideAllContainers();
    viewstudentcontainer.style.display = "block";
});


// Function to handle file input change and preview the selected image
studentPicture.addEventListener("change", function () {
    const file = studentPicture.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            previewImage.style.display = "block";
        };
        reader.readAsDataURL(file);
    } else {
        previewImage.style.display = "none";
    }
});



// Event listener for the form submission (you can add your logic here)
studentForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const studentName = document.getElementById("studentName").value;
    const studentImageFile = studentPicture.files[0];

    // Simulate a successful submission (you should replace this with your actual logic)
    if (studentName && studentImageFile) {
        // Add your logic here to handle the submission, e.g., sending data to a server

        // Display a success alert
        alert("Student added successfully!");

        // Clear the form
        document.getElementById("studentName").value = "";
        studentPicture.value = ""; // Clear the file input
        previewImage.style.display = "none";
    } else {
        // Display an error message if required fields are not filled
        alert("Please fill in all required fields.");
    }
});

function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }