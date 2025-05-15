/**
 * Success Sound Handler
 * This script handles success sounds for the application
 */

const SuccessSoundHandler = {
    /**
     * Initialize the handler
     */
    init: function() {
        // Create audio context
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Preload success sound
        this.loadSuccessSound();
        
        // Override success functions
        this.overrideSuccessFunctions();
    },
    
    /**
     * Load success sound
     */
    loadSuccessSound: function() {
        // Create oscillator for success sound (no need for external file)
        this.successSound = {
            play: () => {
                try {
                    // Create oscillator
                    const oscillator = this.audioContext.createOscillator();
                    const gainNode = this.audioContext.createGain();
                    
                    // Configure oscillator for a pleasant success sound
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(523.25, this.audioContext.currentTime); // C5
                    oscillator.frequency.exponentialRampToValueAtTime(783.99, this.audioContext.currentTime + 0.15); // G5
                    
                    // Configure gain (volume)
                    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    
                    // Connect nodes
                    oscillator.connect(gainNode);
                    gainNode.connect(this.audioContext.destination);
                    
                    // Play sound
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.3);
                    
                    // Add a second tone for a more pleasant success sound
                    setTimeout(() => {
                        const oscillator2 = this.audioContext.createOscillator();
                        const gainNode2 = this.audioContext.createGain();
                        
                        oscillator2.type = 'sine';
                        oscillator2.frequency.setValueAtTime(659.25, this.audioContext.currentTime); // E5
                        oscillator2.frequency.exponentialRampToValueAtTime(1046.50, this.audioContext.currentTime + 0.15); // C6
                        
                        gainNode2.gain.setValueAtTime(0.2, this.audioContext.currentTime);
                        gainNode2.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                        
                        oscillator2.connect(gainNode2);
                        gainNode2.connect(this.audioContext.destination);
                        
                        oscillator2.start();
                        oscillator2.stop(this.audioContext.currentTime + 0.3);
                    }, 100);
                } catch (e) {
                    console.error('Error playing success sound:', e);
                }
            }
        };
    },
    
    /**
     * Override success functions
     */
    overrideSuccessFunctions: function() {
        // Override toast.success if it exists
        if (typeof toast !== 'undefined' && typeof toast.success === 'function') {
            const originalSuccessFunction = toast.success;
            
            toast.success = function() {
                // Play success sound
                SuccessSoundHandler.successSound.play();
                
                // Call original function
                return originalSuccessFunction.apply(this, arguments);
            };
        }
        
        // Override Swal.fire for success cases
        if (typeof Swal !== 'undefined' && typeof Swal.fire === 'function') {
            const originalSwalFire = Swal.fire;
            
            Swal.fire = function() {
                // Check if this is a success dialog
                if (arguments[0] && 
                    (arguments[0].icon === 'success' || 
                     (typeof arguments[0] === 'object' && arguments[0].type === 'success'))) {
                    // Play success sound
                    SuccessSoundHandler.successSound.play();
                }
                
                // Call original function
                return originalSwalFire.apply(this, arguments);
            };
        }
    },
    
    /**
     * Play success sound
     */
    playSuccessSound: function() {
        this.successSound.play();
    }
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize with a slight delay to ensure other scripts are loaded
    setTimeout(() => {
        SuccessSoundHandler.init();
    }, 1000);
});
