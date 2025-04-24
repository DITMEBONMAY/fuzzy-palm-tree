let attemptsRemaining = 3;

document.querySelector("form").onsubmit = async function (event) {
    event.preventDefault();

    // Disable the button
    const submitButton = document.querySelector(".btn");
    submitButton.disabled = true;

    const adminCode = document.getElementById("admin_code").value;

    try {
        const requestData = {
            admin_code: adminCode
        };

        const response = await fetch("/pull_members", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestData)
        });

        const responseData = await response.json();

        if (response.ok) {
            // Reset attempts on successful entry
            attemptsRemaining = 3;

            // Display success message
            const feedback = document.getElementById("feedback");
            feedback.textContent = responseData.message;
            feedback.className = "success-message";

            // Display results if available
            if (responseData.results) {
                feedback.innerHTML += "<ul>";
                responseData.results.forEach(result => {
                    feedback.innerHTML += `<li>${result}</li>`;
                });
                feedback.innerHTML += "</ul>";
            }
        } else {
            handleError(response.status);
        }
    } catch (error) {
        // Handle network errors
        alert("Oops, hacker detected! Better luck next time?");
        window.location.reload();
    } finally {
        // Re-enable the button
        submitButton.disabled = false;
    }
};

function handleError(status) {
    if (status === 429) {
        alert("Rate limit reached. Please try again later.");
    } else if (status === 401) {
        // Decrement attempts
        attemptsRemaining--;

        if (attemptsRemaining > 0) {
            // Show overlay with remaining attempts
            const overlay = document.getElementById("attempts-overlay");
            const messageEl = document.getElementById("attempts-message");
            messageEl.textContent = `${attemptsRemaining} attempt${attemptsRemaining !== 1 ? 's' : ''} remaining`;

            overlay.style.display = 'flex';

            // Hide overlay after 750ms
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 750);
        } else {
            alert("Failed too many times. Reloading the page.");
            window.location.reload();
        }
    } else if (status === 403) {
        alert("Failed too many times. Reloading the page.");
        window.location.reload();
    } else {
        alert("An unexpected error occurred.");
    }
}

// Prevent right-click context menu
document.addEventListener('contextmenu', event => event.preventDefault());

// Prevent text selection
document.addEventListener('selectstart', event => event.preventDefault());

// Block common keyboard shortcuts for viewing source and dev tools
document.addEventListener('keydown', event => {
if ((event.ctrlKey && (['u', 's', 'c', 'a'].includes(event.key.toLowerCase()))) ||
    (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'i') ||
    (event.key === 'F12')) {
    event.preventDefault();
    return false;
}
});