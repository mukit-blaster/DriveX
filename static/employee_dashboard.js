document.addEventListener("DOMContentLoaded", () => {
    const navLinks = document.querySelectorAll(".nav-link");
    const sections = document.querySelectorAll(".section");

    navLinks.forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault(); // Prevent page reload
            const targetId = link.getAttribute("data-target");

            // Hide all sections
            sections.forEach(section => {
                section.classList.remove("visible");
                section.classList.add("hidden");
            });

            // Show the target section
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.remove("hidden");
                targetSection.classList.add("visible");
            }
        });
    });
});


document.getElementById('searchCarForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the form from reloading the page
    
    const query = document.getElementById('search_query').value;

    // Perform AJAX request to search for cars
    fetch('/search_car', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }) // Send the search query in the request body
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        const tableBody = document.querySelector('#searchResults tbody');
        tableBody.innerHTML = ''; // Clear any existing table rows

        // If cars are found, populate the table
        if (data.cars && data.cars.length > 0) {
            data.cars.forEach(car => {
                const row = `
                    <tr>
                        <td>${car.id}</td>
                        <td>${car.carVIN_No}</td>
                        <td>${car.name}</td>
                        <td>${car.model}</td>
                        <td>${car.capacity}</td>
                        <td>${car.color}</td>
                        <td>${car.pickup_point_id}</td>
                    </tr>
                `;
                tableBody.innerHTML += row; // Append each car's data
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="7">No cars found.</td></tr>';
        }
    })
    .catch(error => console.error('Error:', error)); // Log any errors
});