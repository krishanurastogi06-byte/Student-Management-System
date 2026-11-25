let students = [];

function addStudent() {
    let name = document.getElementById("name").value;
    let roll = document.getElementById("roll").value;
    let email = document.getElementById("email").value;
    let course = document.getElementById("course").value;

    if (!name || !roll || !email || !course) {
        alert("Please fill all details!");
        return;
    }

    students.push({ name, roll, email, course });

    displayStudents();

    document.querySelector("form").reset();
}

function displayStudents() {
    let list = document.getElementById("studentList");
    list.innerHTML = "";

    students.forEach((student, index) => {
        list.innerHTML += `
            <tr>
                <td>${student.name}</td>
                <td>${student.roll}</td>
                <td>${student.email}</td>
                <td>${student.course}</td>
                <td>
                    <button onclick="deleteStudent(${index})">Delete</button>
                </td>
            </tr>
        `;
    });
}

function deleteStudent(index) {
    students.splice(index, 1);
    displayStudents();
}