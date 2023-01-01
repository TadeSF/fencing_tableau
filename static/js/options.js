window.location = "options.html"

// Get the width and height of the screen
const screenWidth = window.screen.width;
const screenHeight = window.screen.height;

// Calculate the width and height of the window
const windowWidth = Math.round(screenWidth * 0.6);
const windowHeight = Math.round(screenHeight * 0.4);

// Calculate the top and left position of the window
const windowTop = 0;
const windowLeft = 0;

// Resize and move the window
window.resizeTo(windowWidth, windowHeight);
window.moveTo(windowLeft, windowTop);