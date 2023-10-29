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
    document.getElementById('takeattendanceContentP1').style.display = 'block';
    document.getElementById('takeattendanceContentP2').style.display = 'none';
    
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

  let videoStream;
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let context = canvas.getContext('2d');

        function startCamera() {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(stream => {
                    videoStream = stream;
                    video.srcObject = stream;
                    video.play();
                })
                .catch(err => console.error('Error accessing camera:', err));

            // Show the video element
            video.style.display = 'block';
        }

        function takePicture() {
            if (!videoStream) {
                console.error('Camera not started');
                return;
            }

            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            const imageData = canvas.toDataURL('image/png');

            // Send the image data to the server using Fetch API
            fetch('/save-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ imageData }),
            })
            .then(response => response.json())
            .then(data => console.log('Image saved:', data))
            .catch(error => console.error('Error saving image:', error));
            alert("Student added successfully!");
            document.getElementById("addStudentContentP2").style.display = "none";
            document.getElementById("addStudentContentP1").style.display = "block";
        }


        // Video feed

       // In Video Showing code
       var video_feed = document.getElementById('video-feed');
       video.src = "{{ url_for('video_feed') }}";


    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // Listen for updates to the present list
    socket.on('update_present', function(data) {
        // Update the content of the 'attendance-record' div
        var presentList = data.present.join('\n');
        document.getElementById('attendance-record').innerHTML = presentList;
    });

    // Request an initial update when the page loads
    socket.emit('update_present_request');


    //Submit and next page
    
    // JavaScript function to submit the form and show P2
    function submitFormAndShowP2() {
    const studentName = document.getElementById("studentName").value;
    const studentEmail = document.getElementById("studentEmail").value;

    // Check if required fields are filled
    if (!studentName || !studentEmail) {
        alert("Please fill in all required fields.");
        return;
    }

    const formData = new FormData();
    formData.append("studentName", studentName);
    formData.append("studentEmail", studentEmail);

    // Send the form data to the server using AJAX
    fetch('/submit-student', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Display a success alert
        alert("Student added successfully!");

        // Clear the form
        document.getElementById("studentName").value = "";
        document.getElementById("studentEmail").value = "";

        // Switch to the second part of the "Add Student" content (addStudentContentP2)
        addStudentContentP1.style.display = "none";
        addStudentContentP2.style.display = "block";
    })
}




// Take attendance JS

function showP1Section() {
    document.getElementById('takeattendanceContentP1').style.display = 'block';
    document.getElementById('takeattendanceContentP2').style.display = 'none';
}

// Function to show P2 section and hide P1 section
function showP2Section() {
    document.getElementById('takeattendanceContentP1').style.display = 'none';
    document.getElementById('takeattendanceContentP2').style.display = 'block';
}

// Attach the form submission function to the form's submit event
document.getElementById('attendance-form-take').addEventListener('submit', function (event) {
    event.preventDefault();
    // Assuming you have validation logic here
    // If validation passes, show P2 section
    showP2Section();
});
