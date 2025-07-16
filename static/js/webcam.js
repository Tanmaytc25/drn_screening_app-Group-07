window.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("webcam");
    const startBtn = document.getElementById("startBtn");
    const patientInput = document.getElementById("patientName");
    const statusText = document.getElementById("statusText");
    const progressFill = document.getElementById("progress-bar-fill");

    let flashTimestamp = null;  // to hold actual flash time

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
        })
        .catch(err => {
            statusText.textContent = "Please enable webcam access.";
            console.error("Webcam error: ", err);
        });

    startBtn.addEventListener("click", () => {
        const patient = patientInput.value.trim();
        if (!patient) {
            alert("Please enter a patient name.");
            return;
        }

        statusText.textContent = "Test running...";

        // progress bar setup
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 100) {
                progress += 2;
                progressFill.style.width = progress + "%";
            }
        }, 100);

        // show flash stimulus after delay (1 sec)
        const flashDelay = 1000;
        setTimeout(() => {
            const flash = document.createElement("div");
            flash.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:white;z-index:9999";
            document.body.appendChild(flash);

            //  to record actual flash timestamp here:
            flashTimestamp = Date.now() / 1000;

            // to remove flash after 300ms
            setTimeout(() => flash.remove(), 300);
        }, flashDelay);

        // Wait (to ensure timestamp is captured)
        setTimeout(() => {
            if (!flashTimestamp) {
                statusText.textContent = "❌ Flash timestamp error.";
                return;
            }

            fetch("/run_test", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    flash_timestamp: flashTimestamp,
                    patient_name: patient
                })
            })
            .then(res => {
                clearInterval(progressInterval);
                if (res.ok) {
                    progressFill.style.width = "100%";
                    statusText.innerHTML = `✅ Test completed for ${patient}. <a href="/results/${patient}">View Results</a>`;
                } else {
                    statusText.textContent = "❌ Error occurred while running the test.";
                }
            })
            .catch(err => {
                clearInterval(progressInterval);
                statusText.textContent = "❌ Error occurred while running the test.";
                console.error("Fetch error: ", err);
            });

        }, flashDelay + 400);  // extra wait to ensure flashTimestamp is recorded
    });
});





