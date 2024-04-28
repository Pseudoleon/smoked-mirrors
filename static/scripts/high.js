document.addEventListener('DOMContentLoaded', function() {
    var codeLines = document.querySelectorAll('[id^="codeblockline"]');
    let counter = 1; // Start from 1 because SQL IDs start from 1
    codeLines.forEach(function(line) {
        let lineId = line.getAttribute('id');
        if (lineId == "codeblockline-1") {
            counter++;
        }
    });
    let targetLine = -1;
    codeLines.forEach(function(line) {
        let lineId = line.getAttribute('id');
        if (lineId == "codeblockline-1") {
            counter--;
            let addr = 'http://127.0.0.1:5000/exe/api/' + counter;
            console.log(addr)
            console.log()
            fetch(addr, {
                method: 'GET',
                mode: "no-cors"
            })
            .then(response => response.json())
            .then(data => {
                // Handle response from server
                targetLine = data["message"]["line"] - 1;
                console.log(targetLine);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        line.className += " hover-overlay"
        
        line.addEventListener('click', function() {
            let style = "bg-danger";
            if (lineId == ("codeblockline-" + targetLine)) {
                style = "bg-success";
            } else {
                console.log(lineId)
            }
            line.className += " " + style;
        });
        
    });
});
