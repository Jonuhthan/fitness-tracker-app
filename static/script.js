let videoOn = false;

async function start_video(url) {
    if(!videoOn) {
        videoOn = true;
        // Start feed and swap placeholder with video stream
        await fetch("/start_feed", { method: "POST"});
        document.getElementById("placeholder").src = url;
    }
};

const last_frame = document.getElementById("lastFrame");
last_frame.src = "/last_frame"
console.log(last_frame.src)