document.addEventListener('DOMContentLoaded', function() {
    var codeLines = document.querySelectorAll('[id^="codeblockline"]');

    codeLines.forEach(function(line) {
        line.className += " hover-overlay"
        line.addEventListener('click', function() {
            console.log("clicked!")
        });
    });
});
