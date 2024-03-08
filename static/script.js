async function start_video(url) {
    await fetch("/start_feed", { method: "POST"});
    document.getElementById("placeholder").src = url;
};