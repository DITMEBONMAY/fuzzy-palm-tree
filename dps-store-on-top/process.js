document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('updateForm');
    const loading = document.getElementById('loading');
    const updateButton = document.getElementById('updateButton');
    const successMessage = document.getElementById('successMessage');
    const currentDelivery = document.querySelector('.current-delivery .info-value');
    const deliverySpinner = document.getElementById('deliverySpinner');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const syncIcon = document.getElementById('syncIcon');
  
    // Remove pulse animation on hover
    updateButton.addEventListener('mouseover', () => {
        updateButton.classList.remove('pulse');
    });
  
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        
        // Show loading spinner, disable button, and show progress bar
        loading.style.display = 'inline-block';
        updateButton.disabled = true;
        syncIcon.classList.add('rotating');
        progressContainer.style.display = 'block';
        
        // Add smooth transition to progress bar
        progressBar.style.transition = 'width 0.4s cubic-bezier(0.4, 0.0, 0.2, 1)';
        
        // Show the spinner overlay on the delivery section
        deliverySpinner.style.display = 'flex';
  
        const deliveryDetails = document.getElementById('delivery_details').value;
        const formData = new FormData();
        formData.append('delivery_details', deliveryDetails);
  
        // Improved progress animation
        // Start with quick initial progress to show responsiveness
        progressBar.style.width = '15%';
        
        // Use variable speeds to make the animation more realistic
        const animateProgress = () => {
            let progress = 15;
            let speed = 1; // Initial speed
            let delay = 100; // Initial delay between updates
            
            const acceleration = [
                { threshold: 30, speed: 0.8, delay: 120 },  // Slow down a bit
                { threshold: 50, speed: 0.6, delay: 150 },  // Slow down more
                { threshold: 70, speed: 0.4, delay: 200 },  // Even slower
                { threshold: 85, speed: 0.2, delay: 250 }   // Very slow as we approach 90%
            ];
            
            const progressInterval = setInterval(() => {
                // Adjust speed based on current progress
                for (const point of acceleration) {
                    if (progress < point.threshold) {
                        speed = point.speed;
                        delay = point.delay;
                        break;
                    }
                }
                
                // Add a small random factor for natural feel
                progress += speed * (0.8 + Math.random() * 0.4);
                
                // Cap at 90% until the actual operation completes
                if (progress >= 90) {
                    progress = 90;
                    clearInterval(progressInterval);
                }
                
                progressBar.style.width = `${progress}%`;
            }, delay);
            
            return progressInterval;
        };
        
        const progressInterval = animateProgress();
  
        try {
            // Artificial delay to show the spinning animation (remove in production)
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
  
            // Complete the progress bar with a final satisfying animation
            clearInterval(progressInterval);
            progressBar.style.width = '100%';
  
            if (data.success) {
                // Hide the spinner overlay
                setTimeout(() => {
                    deliverySpinner.style.display = 'none';
                    
                    // Display success message with fade-in effect
                    successMessage.style.display = 'flex';
                    successMessage.style.opacity = '0';
                    successMessage.style.transform = 'translateY(10px)';
                    
                    // Update delivery details with animation
                    currentDelivery.innerHTML = '';
                    let newElement = document.createElement('div');
                    newElement.textContent = data.newDetails;
                    newElement.style.opacity = '0';
                    newElement.style.transform = 'translateY(10px)';
                    currentDelivery.appendChild(newElement);
                    
                    setTimeout(() => {
                        successMessage.style.transition = 'all 0.3s ease';
                        successMessage.style.opacity = '1';
                        successMessage.style.transform = 'translateY(0)';
                        
                        newElement.style.transition = 'all 0.5s ease';
                        newElement.style.opacity = '1';
                        newElement.style.transform = 'translateY(0)';
                    }, 10);
                    
                    // Clear the textarea
                    document.getElementById('delivery_details').value = '';
  
                    // Hide success message after 5 seconds
                    setTimeout(() => {
                        successMessage.style.transition = 'all 0.3s ease';
                        successMessage.style.opacity = '0';
                        successMessage.style.transform = 'translateY(10px)';
                        setTimeout(() => { successMessage.style.display = 'none'; }, 300);
                    }, 5000);
                }, 500);
            } else {
                alert('Failed to update delivery details.');
                deliverySpinner.style.display = 'none';
            }
        } catch (error) {
            console.error('Error updating delivery details:', error);
            alert('An error occurred while updating delivery details.');
            deliverySpinner.style.display = 'none';
        } finally {
            // Hide loading spinner, re-enable the button, and hide progress bar
            setTimeout(() => {
                loading.style.display = 'none';
                updateButton.disabled = false;
                syncIcon.classList.remove('rotating');
                
                // Hide progress bar with a fade-out effect
                progressContainer.style.transition = 'opacity 0.5s ease';
                progressContainer.style.opacity = '0';
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    progressContainer.style.opacity = '1';
                    progressBar.style.transition = '';
                    progressBar.style.width = '0%';
                }, 500);
            }, 500);
        }
    });
  });