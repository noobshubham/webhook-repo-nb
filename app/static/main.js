let lastTimestamp = null;


async function fetchEvents() {

    let url = "/events";

    if (lastTimestamp) {
        url += `?since=${lastTimestamp}`;
    }

    try {

        const res = await fetch(url);
        const data = await res.json();

        if (data.length > 0) {

            renderEvents(data);

            // Update last timestamp
            lastTimestamp = data[0].timestamp;
        }

    } catch (err) {
        console.error("Fetch error:", err);
    }
}


function formatDate(isoString) {

    const date = new Date(isoString);

    return date.toUTCString();
}


function formatEvent(event) {

    const time = formatDate(event.timestamp);

    if (event.action === "PUSH") {

        return `${event.author} pushed to ${event.to_branch} on ${time}`;

    }

    if (event.action === "PULL_REQUEST") {

        return `${event.author} submitted a pull request from ${event.from_branch} to ${event.to_branch} on ${time}`;

    }

    if (event.action === "MERGE") {

        return `${event.author} merged branch ${event.from_branch} to ${event.to_branch} on ${time}`;

    }

    return "";
}


function renderEvents(events) {

    const container = document.getElementById("events");

    events.reverse().forEach(event => {

        const div = document.createElement("div");

        div.className = "event";

        div.textContent = formatEvent(event);

        container.prepend(div);
    });
}


// Initial fetch
fetchEvents();

// Poll every 15 seconds
setInterval(fetchEvents, 15000);

document.getElementById("events").innerHTML = "Loading...";