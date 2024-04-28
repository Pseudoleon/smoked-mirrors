let correctLineMap = {};

document.addEventListener('DOMContentLoaded', async function() {
    var codeLines = document.querySelectorAll('[id^="codeblockline"]');
    let counter = -1; // Start from 1 because SQL IDs start from 1

    let targetLine = -1;
    for (let line of codeLines) {
        let lineId = line.getAttribute('id');
        // console.log("LINE: " + lineId)
        if (lineId == "codeblockline-1") {
            counter++;
            targetLine = -1;
            let addr = 'http://127.0.0.1:5000/exe/api/' + counter;
            console.log(addr);
            await fetch(addr, {
                method: 'GET',
                mode: "no-cors"
            })
            .then(response => response.json())
            .then(data => {
                // Handle response from server
                targetLine = data["message"]["line"];
                console.log("Target line: " + targetLine);

                // console.log("setting " + counter + " to " + targetLine);
                correctLineMap[counter] = targetLine;
                // console.log(correctLineMap);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        line.className += " hover-overlay";
        line.setAttribute("messageID", counter);

        // console.log(correctLineMap);

        line.addEventListener('click', function() {
            let messageID = this.getAttribute("messageID");
            let targ = correctLineMap[messageID];
            let id = this.getAttribute("id");
            
            console.log("click detected for " + id + " of " + messageID + " . target it: " + targ);
            // console.log(correctLineMap);

            let style = "bg-danger";
            if (id == ("codeblockline-" + targ)) {
                style = "bg-success";
            }
            line.className += " " + style;
        });
        
    }
});
