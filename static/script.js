let videoOn = false;

async function start_video(url) {
    if(!videoOn) {
        videoOn = true;
        // Start feed and swap placeholder with video stream
        await fetch("/start_feed", { method: "POST"});
        document.getElementById("placeholder").src = url;
    }
};