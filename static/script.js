let videoOn = false;

async function start_video(url) {
    if(!videoOn) {
        videoOn = true;
        // Start feed and swap placeholder with video stream
        await fetch("/start_feed", { method: "POST"});
        document.getElementById("placeholder").src = url;
    }
};

const scanButton = document.getElementById("scanButton");
const manButton = document.getElementById("manButton");
const barFieldCont = document.getElementById("barFieldCont");

// Makes option to manually enter barcode visible
scanButton.addEventListener("click", () => {
    setTimeout(() => {
        manButton.style.display = 'inline-block';
    }, 7500);
});

// Barcode entry field made visible
manButton.addEventListener("click", () => {
    barFieldCont.style.display = 'block';
});