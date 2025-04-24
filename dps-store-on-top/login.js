let attemptsRemaining = 3;

document.querySelector("form").onsubmit = async function (event) {
  event.preventDefault();
  
  const submitButton = document.querySelector(".btn");
  submitButton.disabled = true;
  submitButton.textContent = "Authenticating...";
  
  // Map form values to expected keys:
  const user_id = document.getElementById("staff_id").value;
  const password = document.getElementById("admin_code").value;
  
  try {
    const requestData = { user_id, password };
    
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "LOGIN-Code": 'jejDRC9ffTXLqeAply00ebA1opzw2h3rCRi3g71eF7aixzMuSlwfxlfarG3j9bqWKH4LJYUF7cnz0fYA0iauTqEZDkrwRfY0J6LK'
      },
      body: JSON.stringify(requestData)
    });
    
    const responseData = await response.json();
    
    if (response.ok && responseData.redirect_url) {
      // Reset attempts and show success feedback
      attemptsRemaining = 3;
      const feedback = document.getElementById("feedback");
      feedback.innerHTML = '<div class="done-animation">✓</div>' + responseData.message;
      feedback.className = "success-message active";
      
      setTimeout(() => {
        window.location.href = responseData.redirect_url;
      }, 1500);
    } else {
      handleError(response.status, responseData.message);
    }
  } catch (error) {
    alert("Security violation detected. This incident will be logged.");
    window.location.reload();
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Login";
  }
};

function handleError(status, message) {
  if (status === 429) {
    alert("Rate limit reached. Please try again later.");
  } else if (status === 401) {
    attemptsRemaining--;
    if (attemptsRemaining > 0) {
      const overlay = document.getElementById("attempts-overlay");
      const messageEl = document.getElementById("attempts-message");
      messageEl.textContent = `${attemptsRemaining} attempt${attemptsRemaining !== 1 ? 's' : ''} remaining`;
      overlay.style.display = "flex";
      overlay.className = "active";
      setTimeout(() => {
        overlay.style.display = "none";
        overlay.className = "";
      }, 1200);
    } else {
      alert("Security violation: Too many invalid attempts. This incident has been logged.");
      window.location.reload();
    }
  } else if (status === 403) {
    alert("Access denied. This incident has been logged.");
    window.location.reload();
  } else {
    alert(message || "System error. Please contact system administrator.");
  }
}

// Prevent context menu, text selection, and common dev tool shortcuts
document.addEventListener("contextmenu", event => event.preventDefault());
document.addEventListener("selectstart", event => event.preventDefault());
document.addEventListener("keydown", event => {
  if (
    (event.ctrlKey && ["u", "s", "c", "a"].includes(event.key.toLowerCase())) ||
    (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === "i") ||
    (event.key === "F12")
  ) {
    event.preventDefault();
    return false;
  }
});