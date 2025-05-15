/**
 * Error Sound Handler
 * This script handles error sounds for the application
 */

const ErrorSoundHandler = {
    /**
     * Initialize the handler
     */
    init: function() {
        // Create audio context
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Preload error sound
        this.loadErrorSound();
        
        // Override error functions
        this.overrideErrorFunctions();
    },
    
    /**
     * Load error sound
     */
    loadErrorSound: function() {
        // Create oscillator for error sound (no need for external file)
        this.errorSound = {
            play: () => {
                try {
                    // Create oscillator
                    const oscillator = this.audioContext.createOscillator();
                    const gainNode = this.audioContext.createGain();
                    
                    // Configure oscillator
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(440, this.audioContext.currentTime); // A4
                    oscillator.frequency.exponentialRampToValueAtTime(220, this.audioContext.currentTime + 0.2); // A3
                    
                    // Configure gain (volume)
                    gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    
                    // Connect nodes
                    oscillator.connect(gainNode);
                    gainNode.connect(this.audioContext.destination);
                    
                    // Play sound
                    oscillator.start();
                    oscillator.stop(this.audioContext.currentTime + 0.3);
                } catch (e) {
                    console.error('Error playing sound:', e);
                }
            }
        };
    },
    
    /**
     * Override error functions
     */
    overrideErrorFunctions: function() {
        // Override toast.error if it exists
        if (typeof toast !== 'undefined' && typeof toast.error === 'function') {
            const originalErrorFunction = toast.error;
            
            toast.error = function() {
                // Play error sound
                ErrorSoundHandler.errorSound.play();
                
                // Call original function
                return originalErrorFunction.apply(this, arguments);
            };
        }
        
        // Override Swal.fire for error cases
        if (typeof Swal !== 'undefined' && typeof Swal.fire === 'function') {
            const originalSwalFire = Swal.fire;
            
            Swal.fire = function() {
                // Check if this is an error dialog
                if (arguments[0] && 
                    (arguments[0].icon === 'error' || 
                     (typeof arguments[0] === 'object' && arguments[0].type === 'error'))) {
                    // Play error sound
                    ErrorSoundHandler.errorSound.play();
                }
                
                // Call original function
                return originalSwalFire.apply(this, arguments);
            };
        }
    },
    
    /**
     * Play error sound
     */
    playErrorSound: function() {
        this.errorSound.play();
    }
};

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize with a slight delay to ensure other scripts are loaded
    setTimeout(() => {
        ErrorSoundHandler.init();
    }, 1000);
});
