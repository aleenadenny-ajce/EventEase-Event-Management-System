/**
 * EventEase — Client-Side Scripts
 * Handles dynamic UI interactions, Chart.js dashboard charts, and form validations.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach((alert) => {
        setTimeout(() => {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = "none";
            }
        }, 5000);
    });

    // 2. Setup Delete Confirmation Prompts
    const deleteForms = document.querySelectorAll("form.delete-confirm");
    deleteForms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const itemName = form.getAttribute("data-item-name") || "this item";
            if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                e.preventDefault();
            }
        });
    });

    // 3. Client-side Form Validation for Event Creation & Editing
    const eventForm = document.getElementById("eventForm");
    if (eventForm) {
        eventForm.addEventListener("submit", (e) => {
            const eventDateInput = document.getElementById("date");
            const deadlineInput = document.getElementById("registration_deadline");
            const startTimeInput = document.getElementById("start_time");
            const endTimeInput = document.getElementById("end_time");
            const capacityInput = document.getElementById("capacity");

            if (eventDateInput && deadlineInput) {
                const eventDate = eventDateInput.value;
                const deadline = deadlineInput.value;

                if (deadline > eventDate) {
                    alert("Validation Error: Registration deadline cannot be after the event date.");
                    deadlineInput.focus();
                    e.preventDefault();
                    return false;
                }
            }

            if (capacityInput && parseInt(capacityInput.value, 10) <= 0) {
                alert("Validation Error: Capacity must be at least 1 participant.");
                capacityInput.focus();
                e.preventDefault();
                return false;
            }
        });
    }

    // 4. Initialize Admin Charts if canvas elements exist
    initAdminCharts();
});

function initAdminCharts() {
    const statusCanvas = document.getElementById("statusChart");
    const categoryCanvas = document.getElementById("categoryChart");

    if (statusCanvas && window.Chart && window.chartData) {
        const statusCtx = statusCanvas.getContext("2d");
        new Chart(statusCtx, {
            type: "doughnut",
            data: {
                labels: Object.keys(window.chartData.status || {}),
                datasets: [{
                    data: Object.values(window.chartData.status || {}),
                    backgroundColor: [
                        "#3b82f6", // Upcoming (Blue)
                        "#10b981", // Completed (Green)
                        "#f59e0b", // Ongoing (Amber)
                        "#ef4444"  // Cancelled (Red)
                    ],
                    borderWidth: 1,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { boxWidth: 12, padding: 15 }
                    }
                }
            }
        });
    }

    if (categoryCanvas && window.Chart && window.chartData) {
        const categoryCtx = categoryCanvas.getContext("2d");
        new Chart(categoryCtx, {
            type: "bar",
            data: {
                labels: Object.keys(window.chartData.category || {}),
                datasets: [{
                    label: "Events",
                    data: Object.values(window.chartData.category || {}),
                    backgroundColor: "#6366f1",
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
}
