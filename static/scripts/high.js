document.addEventListener('DOMContentLoaded', function() {
    var codeLines = document.querySelectorAll('[id^="codeblockline"]');
    let counter = 1;
    codeLines.forEach(function(line) {
        let lineId = line.getAttribute('id');
        if (lineId == "codeblockline-1") {
            counter++;
        }
    });
    
    codeLines.forEach(function(line) {
        if (lineId == "codeblockline-1") {
            counter--;
        }

        line.className += " hover-overlay"
        let lineId = line.getAttribute('id');
        
        line.addEventListener('click', function() {
            // Make API request to /executions/api
            // Process
            console.log("clicked")
        });
        
    });
});
