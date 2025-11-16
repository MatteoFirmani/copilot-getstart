document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const colors = ["#d32f2f", "#f57c00", "#7b1fa2", "#0288d1", "#388e3c", "#c2185b", "#1565c0"];
        const participantsList = details.participants
          .map((email, index) => `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}" style="color: ${colors[index % colors.length]}; border-color: ${colors[index % colors.length]};" title="Remove participant">✕</button></li>`)
          .join("");

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> <span class="availability ${spotsLeft === 0 ? 'full' : 'open'}">${spotsLeft} spots left</span></p>
          <div class="participants-section">
            <strong>Current Participants (${details.participants.length}/${details.max_participants}):</strong>
            <ul class="participants-list">
              ${participantsList}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete participant button clicks
  document.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-btn")) {
      const activity = event.target.getAttribute("data-activity");
      const email = event.target.getAttribute("data-email");

      if (!confirm(`Remove ${email} from ${activity}?`)) {
        return;
      }

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: "DELETE",
          }
        );

        const result = await response.json();

        if (response.ok) {
          messageDiv.textContent = result.message;
          messageDiv.className = "success";
          messageDiv.classList.remove("hidden");
          fetchActivities(); // Refresh the activity list

          // Hide message after 3 seconds
          setTimeout(() => {
            messageDiv.classList.add("hidden");
          }, 3000);
        } else {
          messageDiv.textContent = result.detail || "An error occurred";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
        }
      } catch (error) {
        messageDiv.textContent = "Failed to remove participant. Please try again.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error("Error removing participant:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
