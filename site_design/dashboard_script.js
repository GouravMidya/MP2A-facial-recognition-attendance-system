//dashboard script

const addStudentLink = document.getElementById("addStudentLink");
const currentContent = document.getElementById("currentContent");
const addStudentContent = document.getElementById("addStudentContent");
const studentForm = document.getElementById("studentForm");
const studentPicture = document.getElementById("studentPicture");
const previewImage = document.getElementById("previewImage");

addStudentLink.addEventListener("click", function() {
    // Toggle visibility of the divs
    currentContent.style.display = "none";
    addStudentContent.style.display = "block";
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
