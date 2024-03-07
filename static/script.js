async function start_video(url) {
    await fetch("/start_feed", { method: "POST"});
    document.getElementById("placeholder").src = url;
};

async function stop_video(image) {
    await fetch("/stop_feed", { method: "POST"});
    document.getElementById("placeholder").src = image;
};