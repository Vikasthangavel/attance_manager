document.addEventListener("DOMContentLoaded", function () {
    let video = document.createElement("video");
    let canvasElement = document.getElementById("qr-canvas");
    let canvas = canvasElement.getContext("2d");
    let scanning = false;

    // Start webcam stream
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(function (stream) {
            video.srcObject = stream;
            video.setAttribute("playsinline", true);
            video.play();
            scanning = true;
            scanQRCode();
        });

    function scanQRCode() {
        if (!scanning) return;

        canvasElement.width = video.videoWidth;
        canvasElement.height = video.videoHeight;
        canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

        let imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
        let code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: "dontInvert",
        });

        if (code) {
            scanning = false;
            stopVideoStream();

            let currentPage = document.body.dataset.page;

            if (currentPage === "old") {
                // Store old QR in session and redirect to new QR page
                localStorage.setItem("oldQR", code.data);
                window.location.href = "/new_qr";
            } else if (currentPage === "new") {
                // Store new QR and submit both values to Flask
                let oldQR = localStorage.getItem("oldQR");
                let newQR = code.data;

                fetch("/submit_qr", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ oldQR, newQR }),
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    if (data.status === "success") {
                        window.location.href = "/";
                    }
                });
            }
        } else {
            requestAnimationFrame(scanQRCode);
        }
    }

    function stopVideoStream() {
        let tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
    }
});
